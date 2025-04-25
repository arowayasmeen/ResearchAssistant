import os
import sys

# Add the project root to the Python path to ensure package imports work correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from flask import Flask, request, jsonify
from flask_cors import CORS  # This helps with cross-origin requests

from research_assistant.retrieval.lit_review_engine import search_papers
from research_assistant.ranking.paper_ranker import rank_papers_by_relevance

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})  # Enable CORS for all routes

@app.route('/api/search', methods=['POST'])
def api_search():
    data = request.json
    query = data.get('query', '')
    
    if not query:
        return jsonify({"error": "No query provided"}), 400
    
    try:
        # Use the existing functions
        results = search_papers(query, max_results=3)
        ranked_papers = rank_papers_by_relevance(papers=results, query=query)
        
        # Return only the fields needed for the table
        simplified_results = []
        for paper in ranked_papers:
            simplified_results.append({
                "title": paper.get("title", ""),
                "authors": paper.get("authors", ""),
                "year": paper.get("year", ""),
                "venue": paper.get("venue", ""),
                "link": paper.get("url", ""),
                "score": round(paper.get("relevance_score", 0),2)
            })
        
        return jsonify({"results": simplified_results})
    
    except Exception as e:
        import traceback
        print(f"API error: {e}")
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("Starting Research Assistant API server on http://localhost:5000")
    app.run(debug=True, port=5000)