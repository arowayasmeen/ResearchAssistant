# imports
import os
import json
import csv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from SearchSemanticScholar import get_semantic_scholar_results
from SearchGoogleScholar import get_googlescholar_results

def search_papers(query, max_results=10):
    logger.info(f"Searching papers for query: '{query}'")
    sem_results = get_semantic_scholar_results(query, max_results)
    gs_results = get_googlescholar_results(query, max_results, sem_results)
    return sem_results + gs_results

def export_to_json(papers, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(papers, f, indent=2, ensure_ascii=False)

def export_to_csv(papers, filename):
    if not papers:
        return
    keys = ["title", "url", "year", "venue", "authors", "citations", "abstract"]
    with open(filename, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(papers)

def export_results(results, base_filename="papers"):
    # Ensure folder exists
    os.makedirs("exports", exist_ok=True)

    json_path = f"exports/{base_filename}.json"
    csv_path = f"exports/{base_filename}.csv"

    # Export JSON
    with open(json_path, "w", encoding="utf-8") as f_json:
        json.dump(results, f_json, indent=2, ensure_ascii=False)

    # Export CSV
    if results:
        keys = results[0].keys()
        with open(csv_path, "w", newline='', encoding="utf-8") as f_csv:
            writer = csv.DictWriter(f_csv, fieldnames=keys)
            writer.writeheader()
            writer.writerows(results)

    print(f"✅ Exported results to:\n  • {json_path}\n  • {csv_path}")
def main(query, max_results=10):
    results = search_papers(query, max_results)
    # Export to JSON and CSV
    export_results(results, base_filename=query.replace(" ", "_"))
    return

if __name__ == "__main__":
    query = "Anti-UAV"
    max_results = 20
    main(query, max_results)