import requests

def get_semantic_scholar_results(query, max_results=10):
    '''Search Semantic Scholar for research papers matching the query.
    Args:
        query (str): The search query.
        max_results (int): The maximum number of results to return.
    Returns:
        list: A list of dictionaries containing paper details.
    '''
    url = f"https://api.semanticscholar.org/graph/v1/paper/search" # Semantic Scholar API endpoint
    params = {
        "query": query,
        "limit": max_results,
        "fields": "title,year,venue,authors,url,abstract,citationCount"
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        papers = []
        for paper in response.json().get("data", []):
            papers.append({
                "title": paper.get("title", ""),
                "url": paper.get("url", ""),
                "year": paper.get("year", ""),
                "venue": paper.get("venue", ""),
                "authors": ", ".join([a.get("name", "") for a in paper.get("authors", [])]),
                "citations": paper.get("citationCount", ""),
                "abstract": paper.get("abstract", "")
            })
        return papers
    except Exception as e:
        print(f"Error searching Semantic Scholar: {e}")
        return []