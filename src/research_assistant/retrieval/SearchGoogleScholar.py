# Environment imports
import os
import sys
from dotenv import load_dotenv

# Loading environment variables
load_dotenv()
SERPAPI_KEY = os.environ.get("SERPAPI_KEY").strip('=')[1:-1]

# Add the project root to the Python path to ensure package imports work correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

# Other imports
from serpapi import GoogleScholarSearch
import time
import random
from concurrent.futures import ThreadPoolExecutor

from research_assistant.retrieval.SearchSemanticScholar import get_semantic_scholar_results
from research_assistant.utils.utils import is_duplicate, similar

def enrich_with_semantic_scholar(gs_result):
    '''
    Enrich Google Scholar results with Semantic Scholar data.
    Args:
        gs_result (dict): A single Google Scholar result.
    Returns:
        dict: Enriched result with Semantic Scholar data.
    '''
    time.sleep(random.uniform(0.8, 1.5)) # Random sleep to avoid hitting the API too fast
    query_title = gs_result.get("title", "")
    sem_results = get_semantic_scholar_results(query_title, max_results=1)
    if sem_results:
        top_result = sem_results[0]
        if similar(top_result["title"], query_title) >= 0.9:
            return top_result
    return {
        "title": gs_result.get("title", ""),
        "url": gs_result.get("link", ""),
        "year": "",
        "venue": "",
        "authors": gs_result.get("publication_info", {}).get("summary", ""),
        "citations": gs_result.get("inline_links", {}).get("cited_by", {}).get("total", ""),
        "abstract": gs_result.get("snippet", "")
    }

def enrich_gs_results_parallel(gs_raw_results, sem_results, max_workers=5):
    """This function takes a list of Google Scholar results and enriches them with Semantic Scholar data.
    Args:
        gs_raw_results (list): A list of dictionaries containing Google Scholar results
        sem_results (list): A list of dictionaries containing Semantic Scholar results.
        max_workers (int): Number of threads to use for parallel processing.
    Returns:
        list: List of enriched Google Scholar results.
    """
    # Filter out duplicates first
    unique_gs = [
        res for res in gs_raw_results
        if not is_duplicate(res.get("title", ""), sem_results)
    ]
    # Enrich the results with Semantic Scholar data in parallel
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        enriched_results = list(executor.map(enrich_with_semantic_scholar, unique_gs))
    return enriched_results

def get_googlescholar_results(query, max_results=3, sem_results=None):
    """This function takes a dictionary of parameters and returns a list of dictionaries containing the results from Google Scholar.
    Args:
        query (str): The search query.
        max_results (int): The maximum number of results to return.
        sem_results (list): List of Semantic Scholar results for enrichment.
    Returns:
        list: A list of dictionaries containing Google Scholar results.
    """
    params = {
       "api_key": SERPAPI_KEY,
       "engine": "google_scholar",
        "q": query,
        "hl": "en",
        "start": "0",
        "num": max_results,
        "sort": "relevance"
    }
    try:
        search = GoogleScholarSearch(params)
        results = search.get_dict()
        gs_raw_results = results.get("organic_results", [])
        return enrich_gs_results_parallel(gs_raw_results, sem_results)
    
    except Exception as e:
        print(f"Error fetching Google Scholar results: {e}")
        return []