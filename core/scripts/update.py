import csv
import json
import sys
from pprint import pprint

from my_secrets import secrets

from dspace_rest_client.client import DSpaceClient
from dspace_rest_client.models import Item, Community

# from mysql_conn import MySQLConnection

# Configuration from environment variables
URL = secrets.get("API_URL")
USERNAME = secrets.get("API_USERNAME")
PASSWORD = secrets.get("API_PASSWORD")
ANONYMOUS_UUID = "c8dfffaa-35c9-4dc3-96ea-e0604f4daf04"
KARUUSERS_UUID = "65af854e-b36a-4eac-9565-019818bd8c1e"

d = DSpaceClient(api_endpoint=URL, username=USERNAME, password=PASSWORD, fake_user_agent=True)

def updatePolicies():
    search_results = d.search_objects(query='*:*', dso_type='item', scope='d8594e2d-721c-444a-9d1f-5c2ff143c86e', page=0, size=100)
    print(f"Found {len(search_results)} items")
    for item in search_results:        
            print(f"Item UUID {item.uuid}")
            
            bundle_results = d.get_bundles(uuid=item.uuid, page=0, size=10)
            print(f"Found {len(bundle_results)} bundles")
            for bundle in bundle_results:
                print(f"Bundle UUID {bundle}")
                if bundle.name == "ORIGINAL":
                    bitstream_results = d.get_bitstreams(uuid=bundle.uuid, page=0, size=10)
                    for bitstream in bitstream_results:
                        print(f"Bitstream Name {bitstream.name}")
                        print(f"Bitstream UUID {bitstream.uuid}")
                        print(f"Bitstream Policy {bitstream.resource_policy}")
                        if bitstream.resource_policy is None or len(bitstream.resource_policy) == 0:
                            print(f"Updating Bitstream Policy for {bitstream.name}")
                            policy = {
                                "action": "READ",
                                "groupUUID": KARUUSERS_UUID
                            }
                            try:
                                updated_bitstream = d.add_bitstream_policy(bitstream.uuid, policy)
                                print(f"Updated Bitstream Policy for {bitstream.name}: {updated_bitstream.resource_policy}")
                            except Exception as e:
                                print(f"An error occurred updating bitstream policy: {e}")
                        else:
                            print(f"Bitstream {bitstream.name} already has a policy.")
            print(f"\n===============================\n")
            print(f"\n===============================\n")

def run():
    updatePolicies()

def get_bundles(item_uuid):
    bundles = []
    d.get_bundles(uuid=item_uuid, page=0, size=10)

    return bundles


# def arabicizeJournal(en_name = None):
#     if en_name is None:
#         return None
#     else:
#         if en_name == "The Sciences":
#             return {'ar': 'مجلة العلوم', 'en': 'Journal of Science' }
#         if en_name == "Law and Political Science":
#             return  {'ar': 'مجلة الحقوق والعلوم السياسية', 'en': 'Journal of Law and Political Science' }
#         if en_name == "Languages and Translation":
#             return  {'ar': 'مجلة اللغات والترجمة', 'en': 'Journal of Languages and Translation' }
#         if en_name == "Tourism and Antiquities":
#             return  {'ar': 'مجلة السياحة ولآثار', 'en': 'Journal of Tourism and Archaeology' }
#         if en_name == "Agricultural Sciences":
#             return  {'ar': 'مجلة العلوم الزراعية', 'en': 'Journal of Agricultural Sciences' }
#         if en_name == "Computer and Information Sciences":
#             return  {'ar': 'مجلة علوم الحاسب والمعلومات', 'en': 'Journal of Computer and Information Sciences' }
#         if en_name == "Dental Sciences":
#             return  {'ar': 'مجلة علوم طب الأسنان', 'en': 'Journal of Dental Sciences' }
#         if en_name == "Engineering Sciences":
#             return  {'ar': 'مجلة العلوم الهندسية', 'en': 'Journal of Engineering Sciences' }
#         if en_name == "Management Sciences":
#             return  {'ar': 'مجلة العلوم الإدارية', 'en': 'Journal of Administrative Sciences' }
#         if en_name == "Educational Sciences":
#             return  {'ar': 'مجلة العلوم التربوية', 'en': 'Journal of Educational Sciences and Islamic Studies' }
#         if en_name == "Architecture and Planning":
#             return  {'ar': 'مجلة العمارة والتخطيط', 'en': 'Journal of Architecture and Planning' }
#         if en_name == "Literature":
#             return  {'ar': 'مجلة محو الأمية', 'en': 'Journal of Literature' }
#         if en_name == "Islamic Studies":
#             return  {'ar': 'مجلة الدراسات الإسلامية', 'en': 'Journal of Islamic Studies' }
#         if en_name == "Sports Sciences and Physical Activity":
#             return  {'ar': 'مجلة علوم الرياضة والتربية البدنية', 'en': 'Journal of Sports Sciences and Physical Activity' }
#         if en_name == "Research in Languages & Translation":
#             return  {'ar': 'مجلة البحث في اللغة والترجمة', 'en': 'Journal of Research in Languages & Translation' }

#         else:
#             return None
# def log_errors(txt: str) -> None:
#     try:
#         # Open the file in append mode, creating it if it doesn't exist
#         with open("error.log", 'a', encoding='utf-8') as file:
#             file.write(txt + '\n')
#     except Exception as e:
#         print(f"An error occurred logging errors: {e}")


# search_results = d.search_objects(query='*:*', dso_type='collection', scope='febc04bb-82ba-43e2-bd6f-23a39e39105d', page=0, size=100)
# print(f"Found {len(search_results)} collections")
# for collection in search_results:

#     issue_number = collection.name[:1].strip()
#     en_issue_name = f"Issue {issue_number}"
#     ar_issue_name = f"العدد {issue_number}"

#     new_collections = d.get_collections(uuid=collection.uuid, page=0, size=1)
#     if len(new_collections) == 1:
#         py_collection = new_collections[0]
#         py_collection.metadata['dc.title'] = [
#             {'value': ar_issue_name, 'language': 'ar', 'authority': None, 'confidence': -1, 'place': 0},
#             {'value': en_issue_name, 'language': 'en', 'authority': None, 'confidence': -1, 'place': 0}
#         ]

#         try:
#             updated_collection = d.update_dso(py_collection)
#             print(f"Updated {updated_collection.uuid}")
#         except Exception as e:
#             print(f"An error occurred updating dso error: {e}")

# def updateStatus():
#     search_results = d.search_objects(query='*:*', dso_type='item', scope='febc04bb-82ba-43e2-bd6f-23a39e39105d',
#                                       page=1, size=100)

#     print(f"Found {len(search_results)} items")
#     mysql_conn = MySQLConnection()
#     connection = mysql_conn.connect()
#     cursor = connection.cursor()

#     for item in search_results:

#         source_id = item.metadata.get('dc.identifier.sourceId')[0]['value'] if item.metadata.get('dc.identifier.sourceId') else None
#         if source_id:

#             insert_query = f"""UPDATE `articles` 
#                 SET `status` = 'UPDATED', `item_uuid` = '{item.uuid}'
#                 WHERE `source_id` = '{source_id}';"""
#             try:
#                 cursor.execute(insert_query)
#                 connection.commit()

#                 print(f"Successfully updated {item.uuid}")

#             except Exception as err:
#                 print(f"An error occurred updating {item.uuid} status: {err}")

#         else:
#             print(f"No source_id found for {item.uuid}")

#     connection.close()

def ping():
    mysql_conn = MySQLConnection()
    connection = mysql_conn.connect()
    cursor = connection.cursor()
    insert_query = "SELECT * FROM `articles` LIMIT 10;"
    try:
        print(insert_query)
        cursor.execute(insert_query)
        connection.commit()
        connection.close()
        print(f"Successfully connected")
        return True
    except Exception as err:
        print(f"An error occurred connecting {err}")
        connection.close()
        return err


#
# search_results = d.search_objects(query='*:*', dso_type='community', scope='febc04bb-82ba-43e2-bd6f-23a39e39105d', page=0, size=100)
# print(f"Found {len(search_results)} communities")
# for community in search_results:
#
#     volume_number = community.name[:2].strip()
#     en_volume_name = f"Volume {volume_number}"
#     ar_volume_name = f"المجلد {volume_number}"
#
#     # print(f"Searching for:{ar_volume_name}")
#
#     new_communities = d.get_communities(uuid=community.uuid, page=0, size=1)
#     if len(new_communities) == 1:
#         py_community = new_communities[0]
#         py_community.metadata['dc.title'] = [
#             {'value': ar_volume_name, 'language': 'ar', 'authority': None, 'confidence': -1, 'place': 0},
#             {'value': en_volume_name, 'language': 'en', 'authority': None, 'confidence': -1, 'place': 0}
#         ]
#
#         try:
#             updated_community = d.update_dso(py_community)
#             print(f"Updated {updated_community.uuid}")
#         except Exception as e:
#             print(f"An error occurred updating dso error: {e}")

# Replace 'sample.csv' with the actual path to your CSV file
# file_path = 'metadata_export.csv'

# Read the CSV file
# with open(file_path, 'r', encoding='utf-8-sig') as csv_file:  # utf-8-sig to handle BOM
#     reader = csv.DictReader(csv_file)
#
#     # Iterate through the rows and print each one
#     for row in reader:
#
#         article_uuid = row['id']
#
#         article_response = d.get_item(uuid=article_uuid)
#
#         if article_response is None:
#             print(f"Failed to get article {article_uuid}, skipping.")
#             log_errors(f"Failed to get article {article_uuid}, skipping.")
#             continue
#
#         article = Item(json.loads(article_response.content))
#
#         en_journal_name = article.metadata['dc.relation.journal'][0]['value'] if 'dc.relation.journal' in article.metadata else ""
#         ar_journal_name = row['dc.relation.journal'] if row['dc.relation.journal'] else row['dc.relation.journal[ar]']
#
#         en_volume_name = article.metadata['dc.relation.volume'][0]['value'] if 'dc.relation.volume' in article.metadata else ""
#         ar_volume_name = row['dc.relation.volume'] if row['dc.relation.volume'] else row['dc.relation.volume[ar]']
#
#         en_issue_name = article.metadata['dc.relation.issue'][0]['value'] if 'dc.relation.issue' in article.metadata else ""
#         ar_issue_name = row['dc.relation.issue'] if row['dc.relation.issue'] else row['dc.relation.issue[ar]']
#
#         article.metadata['dc.relation.journal'] = [
#             {"value": ar_journal_name, "language": "ar", "authority": None, "confidence": -1},
#             {"value": en_journal_name, "language": "en", "authority": None, "confidence": -1}
#         ]
#         article.metadata['dc.relation.volume'] = [
#             {"value": ar_volume_name, "language": "ar", "authority": None, "confidence": -1},
#             {"value": en_volume_name, "language": "en", "authority": None, "confidence": -1}
#         ]
#         article.metadata['dc.relation.issue'] = [
#             {"value": ar_issue_name, "language": "ar", "authority": None, "confidence": -1},
#             {"value": en_issue_name, "language": "en", "authority": None, "confidence": -1}
#         ]
#         article.metadata['dc.publisher'] = [
#             {"value": "دار جامعة الملك سعود للنشر", "language": "ar", "authority": None, "confidence": -1},
#             {"value": "King Saud University Press", "language": "en", "authority": None, "confidence": -1}
#         ]
#
#         try:
#             updated_article = d.update_item(item=article)
#             print(f"Updated article {article_uuid}")
#         except Exception as e:
#             print(f"Failed to update article {article_uuid}: {e}")
#             log_errors(f"Failed to update article {article_uuid}: {e}")

