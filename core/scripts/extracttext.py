import os
import json
from PyPDF2 import PdfReader
from django.conf import settings


# Path to store output JSON (you can adjust this)
OUTPUT_JSON = "extracted_texts.json"


def run():
    """
    Extracts text from the first page of all PDF files in a folder
    and appends results to a JSON file.
    Run with: python manage.py runscript extracttext
    """

    # folder_path = input("Enter full folder path containing PDFs: ").strip('"').strip("'")
    folder_path = os.path.join(settings.BASE_DIR, "resources", "pastpapers")

    if not os.path.isdir(folder_path):
        print(f"❌ Invalid folder path: {folder_path}")
        return

    # Load existing data if file exists
    if os.path.exists(OUTPUT_JSON):
        with open(OUTPUT_JSON, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
        data = []

    processed_files = {entry["file"] for entry in data}

    for filename in os.listdir(folder_path):
        if not filename.lower().endswith(".pdf"):
            continue

        if filename in processed_files:
            print(f"⏭ Skipping (already processed): {filename}")
            continue

        pdf_path = os.path.join(folder_path, filename)

        try:
            reader = PdfReader(pdf_path)
            if not reader.pages:
                print(f"⚠ No pages in {filename}")
                continue

            first_page = reader.pages[0]
            text = first_page.extract_text() or ""

            # Clean up text a little
            text = text.strip().replace("\n\n", "\n")

            data.append({
                "file": filename,
                "text": text
            })

            print(f"✅ Extracted from: {filename}")

        except Exception as e:
            print(f"❌ Error reading {filename}: {e}")

    # Write all data back to JSON
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n✨ Extraction complete! Data saved to {OUTPUT_JSON}")
