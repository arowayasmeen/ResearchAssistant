# imports
from SearchSemanticScholar import get_semantic_scholar_results
from SearchGoogleScholar import get_googlescholar_results

def search_papers(query, max_results=10):
    sem_results = get_semantic_scholar_results(query, max_results)
    gs_results = get_googlescholar_results(query, max_results, sem_results)
    return sem_results + gs_results