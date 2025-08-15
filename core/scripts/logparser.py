import os
import re
import csv
from django.conf import settings

# Regex for Apache combined log format
log_pattern = re.compile(
    r'(?P<ip>\S+) \S+ \S+ \[(?P<datetime>[^\]]+)\] '
    r'"(?:GET|POST) (?P<path>\S+)'
)

input_file  = os.path.join(settings.BASE_DIR, "core", "scripts","opacaccess.log")
output_file = os.path.join(settings.BASE_DIR, "core", "scripts","structuredopacaccess.csv")

extracted_data = []

def run():

    with open(input_file, "r", encoding="utf-8") as infile:
        for line in infile:
            match = log_pattern.search(line)
            if match:
                extracted_data.append([
                    match.group("ip"),
                    match.group("datetime"),
                    match.group("path")
                ])

    # Write to CSV
    with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["IP Address", "DateTime", "Path"])
        writer.writerows(extracted_data)

    print(f"Extracted {len(extracted_data)} entries to {output_file}")
