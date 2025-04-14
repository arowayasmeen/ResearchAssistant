import requests

def get_semantic_scholar_results(query, max_results=10):
    url = f"https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        "query": query,
        "limit": max_results,
        "fields": "title,year,venue,authors,url,abstract,citationCount"
    }
    response = requests.get(url, params=params)
    papers = []
    if response.status_code == 200:
        data = response.json()
        for paper in data.get("data", []):
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