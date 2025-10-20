import json
import os
import requests
import time
import re
from django.conf import settings

# CONFIG
OLLAMA_API_URL = "http://127.0.0.1:11434/api/generate"
# MODEL_NAME = "orca-mini:3b"
MODEL_NAME = "phi3:mini"
# MODEL_NAME = "deepseek-r1:1.5b"
INPUT_FILE = os.path.join(settings.BASE_DIR, "extracted_texts.json")
OUTPUT_FILE = os.path.join(settings.BASE_DIR, "structured_metadata.json")
MAX_RECORDS = 5  # Limit processing to first 10 records for now

def clean_text(text):
    # Remove non-printable/control characters
    text = re.sub(r'[^\x20-\x7E]+', ' ', text)

    # Remove any whitespace character (spaces, tabs, newlines, carriage returns, etc.)
    text = re.sub(r'\s+', ' ', text)

    # Strip leading/trailing spaces
    return text.replace('KARATINA UNIVERSITY', '').strip()

def run():
    if not os.path.exists(INPUT_FILE):
        print(f"❌ Input file not found: {INPUT_FILE}")
        return

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        records = json.load(f)

    # Limit to first MAX_RECORDS
    records = records[:MAX_RECORDS]

    results = []
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            try:
                results = json.load(f)
            except json.JSONDecodeError:
                results = []

    print(f"🧩 Processing {len(records)} records using model {MODEL_NAME}...")

    for record in records:
        text = record.get("text", "").strip()
        if not text:
            continue

        prompt = f"""
        You are a metadata extraction assistant for an academic library repository.
        Your task is to extract structured metadata from the text of university examination papers.
        Each paper contains details like:
          program_name e.g., Bachelor or Science in Actuarial Sciene or Diploma in Animan Health;
          coursetitle e.g., Bovine Anatomy II or Introduction to the Theory of Insurance;
          coursecode e.g., ACS 202 or HTT 8228;
          studylevel e.g., Certificate or Diploma or Bachelors or Masters or PhD or Postgraduate Diploma (these are the only 6 possible values);
          yearofstudy e.g., First Year or Second Year or Third Year or Fourth Year or Fifth Year or Sixth Year (these are the only 6 possible values);
          semester e.g., Fist Semester or Second Semester (these are the only 2 possible values);
          academicyear e.g., 2016/2017 or 2025/2026;
          examtype e.g., Main Exam or Regular Exam or Supplementary Exam or Special Exam (these are the only 4 possible values).
        Your task is to extract metadata from the text below and return a JSON object with these exact keys:
        {{
            "program_name": "Master of Education in Educational Psychology",
            "coursetitle": "Managerial Accounting II",
            "coursecode": "BAS 603",
            "studylevel": "Masters",
            "examtype": "Regular Examination",
            "academicyear": "2015/2016",
            "yearofstudy": "Third Year",
            "semester": "Second Semester"
        }}
        Example text:
        UNIVERSITY EXAMINATIONS 2016/2017  ACADEMIC YEAR EXAM FOR  FOURTH YEAR  BACHELOR OF ECONOMICS  COURSE CODE: ECO 422 COURSE TITTLE: PROJECT APPRAISAL AND EVALUATION  DATE DEC…//2016     TIME: 3HR……  INSTRUCTIONS TO CA NDIDATES  Attempt question  ONE  and any other  THREE questions.  Time; 3 hours

        Example output:
        {{
            "program_name": "Bachelor of Economics",
            "coursetitle": "Project Appraisal and Evaluation",
            "coursecode": "ECO 422",
            "studylevel": "Bachelors",
            "examtype": "Regular Exam",
            "academicyear": "2016/2017",
            "yearofstudy": "Fourth Year",
            "semester": "First Semester"
        }}
        Now extract metadata from this text:
        \"\"\"{text}\"\"\"

        Return ONLY a valid JSON object. Do not include any explanations or text outside the JSON even when there are errors.
        """

        payload = {
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False
        }

        start_time = time.time()

        try:
            response = requests.post(OLLAMA_API_URL, json=payload, timeout=120)
            response.raise_for_status()
            data = response.json()

            output_text = data.get("response", "").strip()

            try:
                metadata = json.loads(output_text)
            except json.JSONDecodeError:
                print(f"⚠️ Non-JSON output for file {record['file']}: {output_text}")
                metadata = {"raw_output": output_text}

            metadata["file"] = record["file"]
            metadata["processing_time"] = round(time.time() - start_time, 2)

            results.append(metadata)

            print(f"✅ Processed {record['file']} in {metadata['processing_time']}s")

            # Save incrementally
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)

        except requests.RequestException as e:
            print(f"❌ Error processing {record['file']}: {e}")

    print(f"🎯 Done! Structured metadata for {len(records)} files saved to {OUTPUT_FILE}")
