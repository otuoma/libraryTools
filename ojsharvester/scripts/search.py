import re
from my_secrets import secrets
from dspace_rest_client.client import DSpaceClient, Item, Bundle, Bitstream

# URL = secrets.get("API_URL")
URL = "https://pc.tail34a2d7.ts.net/server/api"
USERNAME = secrets.get("API_USERNAME")
PASSWORD = secrets.get("API_PASSWORD")
d = DSpaceClient(api_endpoint=URL, username=USERNAME,
                 password=PASSWORD, fake_user_agent=True)


def run():
    journal_uuid = 'e06af157-5193-498c-8eb8-9223f6d19480'  # example journal UUID
    issue_name = "Vol. 1 No. 1 (2016)"
    issue_uuid = get_issue_uuid(issue_name, journal_uuid)
    collections = []
    print(f"Issue UUID: {issue_uuid}")

    # search_results = d.search_objects(
    #     query=f"{issue_name}", dso_type='item', page=0, size=500)
    # results_count = len(search_results)
    # print(
    #     f"=========Found {results_count} issues matching '{issue_name}'==========")
    # for collection in search_results:
    #     collections.append({
    #         "collection_name": collection.name,
    #         "collection_uuid": collection.uuid
    #     })
    return collections


def get_issue_uuid(issue_name: str, journal_uuid: str) -> str | None:
    search_filters = {
        'f.entityType': 'JournalIssue,equals',
        # 'f.title': f'"{issue_name}",equals',
        'f.title': "Vol. 1 No. 2,equals",
    }
    search_results = d.search_objects(
        query=f"*:*",
        dso_type='item',
        page=0,
        size=10,
        filters=search_filters,
    )
    print(
        f"Search results for issue '{issue_name}': Found {len(search_results)} issues.")
    for item in search_results:
        metadata = item.metadata

        issue_details = {
            "title": metadata.get('dc.title', [''])[0].get('value', '') if metadata.get('dc.title', [''])[0] else '',
            "issue_uuid": item.uuid,
            "url": metadata.get('dc.identifier.uri', [''])[0].get('value', '') if metadata.get('dc.identifier.uri', [''])[0] else '',
            "issue": metadata.get('publicationissue.issueNumber', [''])[0].get('value', '') if metadata.get('publicationissue.issueNumber', [''])[0] else '',
        }
        print(f"Checking item: {issue_details}")
        print(f"\n=============================================\n")
        if item.name == issue_name:
            return item.uuid
    return None
