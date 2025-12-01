# libraryTools AI Guide
## Project Shape
- Django 5.2 project under `config/` with two apps: `core` for data-processing scripts and `ojsharvester` for OAI-PMH harvesting.
- SQLite (`db.sqlite3`) is the default store; scripts read/write JSON files (`extracted_texts.json`, `structured_metadata.json`) at repo root.
- `django-extensions` is installed and all automation is exposed as `python manage.py runscript <name>` tasks inside each app's `scripts/` package.

## Local Environment
- Install deps with `pip install -r requirements.txt`; add `sickle` manually when working on the harvester (not yet listed in requirements).
- Dev server: `python manage.py runserver`; migrations use the standard `makemigrations`/`migrate` flow and no custom settings modules exist yet.
- Use ASCII when editing unless a file already relies on Unicode; JSON outputs should remain UTF-8 but avoid introducing control characters.

## Data Pipelines (core)
- `core/scripts/extracttext.py` scans `resources/pastpapers/` for PDFs, extracts page 1 via `PyPDF2`, and appends to `extracted_texts.json`; it skips files already present in that JSON.
- `core/scripts/extract_metadata.py` posts exam text to a local Ollama model (`http://127.0.0.1:11434/api/generate` using `model=phi3:mini`). Expect occasional non-JSON responses—code captures them under `raw_output`.
- When updating these scripts, keep incremental writes and the `processing_time` metric so interrupted runs leave usable progress.

## OAI Harvester (ojsharvester)
- `ojsharvester/scripts/oai_harvest.py` demonstrates pulling `ListRecords` from `https://www.rjikm.org/index.php/rjikm/oai` with Sickle and prints the first record.
- `ojsharvester/views.HarvestIssue` wraps Sickle for web use but currently requires a `base_url` argument in `__init__`; `HarvestIssue.as_view()` will fail until that is refactored. Treat it as WIP unless you supply the base URL yourself.
- `ojsharvester/scripts/sample.xml` shows the expected OAI-DC record structure (titles, creators, DC subjects) for parsing logic.

## Conventions
- Place reusable harvest/parsing helpers inside the relevant app and surface runnable scripts through `runscript`; avoid scattering standalone utilities.
- Favor small, side-effect free helpers (e.g., `clean_text`, `parse_ojs_record`) to keep runscripts testable and to simplify retrying failed records.
- Persist derived datasets (`structured_metadata.json`, CSV logs) in repo root or the script folder so subsequent scripts can chain off them without extra path config.

## Testing & Debugging
- No formal tests yet; sanity-check scripts with `python manage.py shell_plus` or ad-hoc runscripts before wiring into views.
- When diagnosing metadata extraction, log the offending `record['file']` and preserve the raw Ollama response for manual cleanup, matching the existing pattern in `extract_metadata.py`.
- Watch for long-running scripts; they use synchronous HTTP calls, so consider chunking `records` before adding concurrency.
