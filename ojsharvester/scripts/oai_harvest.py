import json
import os
import re

from django.conf import settings
from sickle import Sickle
from sickle.oaiexceptions import NoRecordsMatch


BASE_URL = "https://www.rjikm.org/index.php/rjikm/oai"
METADATA_PREFIX = "oai_dc"
OUTPUT_FILE = os.path.join(settings.BASE_DIR, "oai_dc_records.json")
ARTICLES_OUTPUT_FILE = os.path.join(settings.BASE_DIR, "harvested_articles.json")
BATCH_SIZE = 10
MAX_RECORDS = 60
DC_TERMS = [
    "title",
    "creator",
    "subject",
    "description",
    "publisher",
    "contributor",
    "date",
    "type",
    "format",
    "identifier",
    "source",
    "language",
    "relation",
    "coverage",
    "rights",
]


def _clean_value(value):
    if value is None:
        return None
    cleaned = re.sub(r"\s+", " ", value).strip()
    return cleaned or None


def _extract_dc_metadata(record):
    dc_payload = {}
    for term in DC_TERMS:
        raw_values = record.metadata.get(term, []) if record.metadata else []
        cleaned_values = []
        for raw in raw_values:
            cleaned = _clean_value(raw)
            if cleaned and cleaned not in cleaned_values:
                cleaned_values.append(cleaned)
        if cleaned_values:
            dc_payload[term] = cleaned_values
    return dc_payload


def _serialise_record(record):
    header = record.header
    return {
        "header": {
            "identifier": getattr(header, "identifier", None),
            "datestamp": getattr(header, "datestamp", None),
            "sets": list(getattr(header, "setSpecs", []) or []),
            "deleted": bool(getattr(header, "deleted", False)),
        },
        "metadata": _extract_dc_metadata(record),
    }


def _parse_source_fields(source_values):
    if not source_values:
        return {
            "journal_name": None,
            "volume": None,
            "issue_label": None,
            "issue_number": None,
            "pages": None,
            "issn": None,
            "year": None,
        }

    source_text = source_values[0]
    parts = [p.strip() for p in source_text.split(";") if p.strip()]
    journal_name = parts[0] if parts else None
    issue_label = parts[1] if len(parts) > 1 else None
    pages = parts[2] if len(parts) > 2 else None

    vol_match = re.search(r"Vol\.?\s*(\d+)", issue_label or "", flags=re.IGNORECASE)
    volume = vol_match.group(1) if vol_match else None
    issue_match = re.search(r"No\.?\s*(\d+)", issue_label or "", flags=re.IGNORECASE)
    issue_number = issue_match.group(1) if issue_match else None
    year_match = re.search(r"\((\d{4})\)", issue_label or "")
    year = year_match.group(1) if year_match else None

    issn = None
    for entry in source_values:
        match = re.search(r"\b\d{4}-\d{3}[\dXx]\b", entry)
        if match:
            issn = match.group(0)
            break

    return {
        "journal_name": journal_name,
        "volume": volume,
        "issue_label": issue_label,
        "issue_number": issue_number,
        "pages": pages,
        "issn": issn,
        "year": year,
    }


def _parse_rights_fields(rights_values):
    rights_holder = None
    rights_url = None

    if rights_values:
        rights_holder = rights_values[0]
        # holder_match = re.search(
        #     r"Copyright\s*\(c\)\s*\d{4}\s*(.+?)(?:\s*\(|$)", first_entry, flags=re.IGNORECASE
        # )
        # rights_holder = holder_match.group(1).strip() if holder_match else _clean_value(first_entry)

        for entry in rights_values:
            url_match = re.search(r"https?://[^\s]+", entry)
            if url_match:
                rights_url = url_match.group(0)
                break

    return rights_holder, rights_url


def run(output_path=OUTPUT_FILE, base_url=BASE_URL, metadata_prefix=METADATA_PREFIX):
    """Harvest OAI-PMH records and persist Dublin Core fields to JSON."""
    sickle = Sickle(base_url)
    harvested_records = []
    issue_groups = {}
    total_processed = 0
    resumption_token = None

    try:
        while total_processed < MAX_RECORDS:
            params = {"metadataPrefix": metadata_prefix} if resumption_token is None else {"resumptionToken": resumption_token}
            records = sickle.ListRecords(**params)
            batch_processed = 0

            for record in records:
                serialised = _serialise_record(record)
                harvested_records.append(serialised)

                header = serialised["header"]
                metadata = serialised["metadata"]

                if header.get("deleted"):
                    total_processed += 1
                    batch_processed += 1
                    if total_processed >= MAX_RECORDS or batch_processed >= BATCH_SIZE:
                        break
                    continue

                title = metadata.get("title", ["<no title>"])[0]
                authors = metadata.get("creator", [])
                abstract = metadata.get("description", ["<no abstract>"])[0]
                date = metadata.get("date", [None])[0]
                keywords = metadata.get("subject", [])
                publisher = metadata.get("publisher", [None])[0]
                fmt = metadata.get("format", [None])[0]
                identifiers = metadata.get("identifier", [])
                language_values = metadata.get("language", [])
                primary_language = language_values[0] if language_values else None
                relation_values = metadata.get("relation", [])
                relation_link = relation_values[0] if relation_values else None
                rights_values = metadata.get("rights", [])

                source_values = metadata.get("source", [])
                source_info = _parse_source_fields(source_values)
                rights_holder, rights_url = _parse_rights_fields(rights_values)

                issue_key = "|".join(
                    [
                        source_info.get("journal_name") or "",
                        source_info.get("volume") or "",
                        source_info.get("issue_number") or "",
                        source_info.get("year") or "",
                    ]
                )

                issue_group = issue_groups.setdefault(
                    issue_key,
                    {
                        "journal_name": source_info.get("journal_name"),
                        "volume": source_info.get("volume"),
                        "issue_label": source_info.get("issue_label"),
                        "issue_number": source_info.get("issue_number"),
                        "year": source_info.get("year"),
                        "issn": source_info.get("issn"),
                        "articles": [],
                    },
                )

                article_payload = {
                    "oai_identifier": header.get("identifier"),
                    "title": title,
                    "authors": authors,
                    "abstract": abstract,
                    "date": date,
                    "keywords": keywords,
                    "publisher": publisher,
                    "format": fmt,
                    "identifiers": identifiers,
                    "language": primary_language,
                    "relation": relation_link,
                    "pages": source_info.get("pages"),
                    "rights_holder": rights_holder,
                    "rights_url": rights_url,
                }

                issue_group["articles"].append(article_payload)

                print(f"harvested: {title}")

                total_processed += 1
                batch_processed += 1

                if total_processed >= MAX_RECORDS or batch_processed >= BATCH_SIZE:
                    break

            token_obj = getattr(records, "resumption_token", None)
            resumption_token = getattr(token_obj, "token", None) if token_obj else None

            if not resumption_token or total_processed >= MAX_RECORDS:
                break

    except NoRecordsMatch:
        print("no records matched the supplied parameters")
        return
    except Exception as exc:
        print(f"harvest failed: {exc}")
        return

    if not harvested_records:
        print("no records harvested")
        return

    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(harvested_records, handle, indent=2, ensure_ascii=False)

    issues_payload = []
    for issue_key, payload in issue_groups.items():
        issues_payload.append({"issue_key": issue_key, **payload})
        # check if issue item exists on dspace

    with open(ARTICLES_OUTPUT_FILE, "w", encoding="utf-8") as handle:
        json.dump(issues_payload, handle, indent=2, ensure_ascii=False)

    print(f"saved {len(harvested_records)} records to {output_path}")
    print(f"saved {len(issues_payload)} issue groups to {ARTICLES_OUTPUT_FILE}")