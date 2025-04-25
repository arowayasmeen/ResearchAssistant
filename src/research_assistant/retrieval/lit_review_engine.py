# imports
import os
import sys

# Add the project root to the Python path to ensure package imports work correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from research_assistant.retrieval.SearchSemanticScholar import get_semantic_scholar_results
from research_assistant.retrieval.SearchGoogleScholar import get_googlescholar_results

def search_papers(query, max_results=3):
    sem_results = get_semantic_scholar_results(query, max_results)
    gs_results = get_googlescholar_results(query, max_results, sem_results)
    return sem_results + gs_results