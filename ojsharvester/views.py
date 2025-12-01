from django.shortcuts import render
from django.views.generic import View
from sickle import Sickle


# Create your views here.

class HarvestIssue(View):
    
    # def __init__(self, base_url):
    def __init__(self,):
        self.sickle = Sickle('https://www.rjikm.org/index.php/rjikm/oai')

    def ListRecords(self, metadata_prefix="oai_dc", from_date=None):
        params = {"metadataPrefix": metadata_prefix}
        if from_date:
            params["from"] = from_date

        return self.sickle.ListRecords(**params)

    def get_new_records(self, last_harvest_date):
        return self.ListRecords(metadata_prefix="oai_dc", from_date=last_harvest_date)
    
    def parse_ojs_record(record):
        md = record.metadata
        return {
            "title": md.get("title", [""])[0],
            "authors": md.get("creator", []),
            "abstract": md.get("description", [""])[0],
            "doi": md.get("identifier", [""])[0] if "doi" in md else None,
            "date": md.get("date", [""])[0],
            "keywords": md.get("subject", []),
        }
