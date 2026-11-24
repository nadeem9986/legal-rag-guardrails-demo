"""One-time scrape of the 3 legaldesk.com pages used by the comparison (uses the original scraper, 1s delay).
   The scraped text is third-party content, so it is not committed to this repo. Run this once:
       python scrape_corpus.py
   The site changes over time, so a later scrape may differ from the one the stored results were made with."""
import json, os, sys
here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(here, "before"))
from src.utils.scraper import LegalDocumentScraper
docs = LegalDocumentScraper().scrape_all_documents(max_documents=3)
os.makedirs(os.path.join(here, "data"), exist_ok=True)
json.dump(docs, open(os.path.join(here, "data", "docs.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("saved", len(docs), "documents")
