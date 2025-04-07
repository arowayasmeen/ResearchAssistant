from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from dotenv import load_dotenv

# Import the search functions from provided scripts
from SearchArxiv import get_arxiv_results
from SearchGoogleScholar import get_googlescholar_results

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend-backend communication

# Load environment variables
load_dotenv()
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

@app.route('/api/search', methods=['POST'])
def search_papers():
    """
    API endpoint to search for papers using Arxiv and/or Google Scholar
    Expects JSON with:
        - query: search term
        - use_google_scholar: boolean
        - use_arxiv: boolean
    """
    data = request.json
    query = data.get('query', '')
    use_google_scholar = data.get('use_google_scholar', False)
    use_arxiv = data.get('use_arxiv', False)
    
    if not query:
        return jsonify({"error": "No query provided"}), 400
    
    results = []
    
    # Search Arxiv if selected
    if use_arxiv:
        try:
            arxiv_results = get_arxiv_results(query, max_results=5)
            results.extend(arxiv_results)
        except Exception as e:
            print(f"Error searching ArXiv: {e}")
    
    # Search Google Scholar if selected
    if use_google_scholar and SERPAPI_KEY:
        try:
            scholar_params = {
                "api_key": SERPAPI_KEY,
                "engine": "google_scholar",
                "q": query,
                "hl": "en",
                "num": 5
            }
            google_results = get_googlescholar_results(scholar_params)
            
            # Format Google Scholar results to match Arxiv format
            for result in google_results:
                results.append({
                    "title": result["title"],
                    "link": result["link"]
                })
        except Exception as e:
            print(f"Error searching Google Scholar: {e}")
    
    return jsonify({"results": results})

if __name__ == '__main__':
    # To run this backend server:
    # 1. Install requirements: pip install flask flask-cors python-dotenv requests serpapi
    # 2. Make sure SearchArxiv.py and SearchGoogleScholar.py are in the same directory
    # 3. Create .env file with SERPAPI_KEY=your_api_key
    # 4. Run this file: python app.py
    app.run(debug=True)