# Environment imports
import os
from dotenv import load_dotenv

# Loading environment variables
load_dotenv()
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

# Other imports
from serpapi import GoogleScholarSearch
from urllib.parse import urlsplit, parse_qsl

def get_googlescholar_results(query, max_results=10):
    """This function takes a dictionary of parameters and returns a list of dictionaries containing the results from Google Scholar."""
    params = {
       "api_key": SERPAPI_KEY,
       "engine": "google_scholar",
        "q": query,
        "hl": "en",
        "start": "0"
    }
    search = GoogleScholarSearch(params)

    googlescholar_results_data = []

    loop_is_true = True

    count = 0

    while loop_is_true:
        results = search.get_dict()

        for result in results["organic_results"]:
            title = result["title"]
            link = result.get("link")

            googlescholar_results_data.append({
              "title": title,
              "link": link
            })
            count += 1

        if "next" in results.get("serpapi_pagination", {}) and count < max_results:
            search.params_dict.update(dict(parse_qsl(urlsplit(results["serpapi_pagination"]["next"]).query)))
        else:
            loop_is_true = False

    return googlescholar_results_data