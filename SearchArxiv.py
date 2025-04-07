# Necessary imports
import requests
import xml.etree.ElementTree as ET

def get_arxiv_results(query, max_results=10):
    """Search Arxiv for research papers matching the query."""
    base_url = "http://export.arxiv.org/api/query"
    params = {
        "search_query": query,
        "start": 0,
        "max_results": max_results,
        "sortBy": "relevance",
        "sortOrder": "descending"
    }
    response = requests.get(base_url, params=params)
    if response.status_code != 200:
        raise Exception("Failed to retrieve data from ArXiv API")
    
    root = ET.fromstring(response.text)
    
    arxiv_results_data = []
    for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
        title = entry.find("{http://www.w3.org/2005/Atom}title").text
        link = entry.find("{http://www.w3.org/2005/Atom}id").text
        
        arxiv_results_data.append({
            "title": title.strip(),
            "link": link.strip()
        })
    
    return arxiv_results_data