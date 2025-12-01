import json
import os
import re

from django.conf import settings
from sickle import Sickle
from sickle.oaiexceptions import NoRecordsMatch


BASE_URL = "https://www.rjikm.org/index.php/rjikm/oai"
METADATA_PREFIX = "oai_dc"
OUTPUT_FILE = os.path.join(settings.BASE_DIR, "oai_dc_records.json")
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


def run(output_path=OUTPUT_FILE, base_url=BASE_URL, metadata_prefix=METADATA_PREFIX):
    """Harvest OAI-PMH records and persist Dublin Core fields to JSON."""
    sickle = Sickle(base_url)
    harvested = []
    max_records = 10

    try:
        iterator = sickle.ListRecords(metadataPrefix=metadata_prefix)
        for index, record in enumerate(iterator, start=1):
            serialised = _serialise_record(record)
            harvested.append(serialised)
            print(f"harvested: {serialised['header']['identifier']}")
            if max_records and index >= max_records:
                break
    except NoRecordsMatch:
        print("no records matched the supplied parameters")
        return
    except Exception as exc:
        print(f"harvest failed: {exc}")
        return

    if not harvested:
        print("no records harvested")
        return

    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(harvested, handle, indent=2, ensure_ascii=False)

    print(f"saved {len(harvested)} records to {output_path}")