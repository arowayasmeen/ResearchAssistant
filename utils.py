from difflib import SequenceMatcher

def similar(a, b):
    '''
    Calculate the similarity between two strings using SequenceMatcher.
    Args:
        a (str): First string.
        b (str): Second string.
    Returns:
        float: Similarity ratio between 0 and 1.
    '''
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def is_duplicate(gs_title, sem_results, threshold=0.9):
    '''
    Check if a Google Scholar title is similar to any title in the Semantic Scholar results.
    If the similarity is above the threshold, it is considered a duplicate.
    Args:
        gs_title (str): Title from Google Scholar.
        sem_results (list): List of Semantic Scholar results.
        threshold (float): Similarity threshold to consider as duplicate.
    Returns:
        bool: True if duplicate, False otherwise.
    '''
    return any(similar(gs_title, sem_paper['title']) >= threshold for sem_paper in sem_results)