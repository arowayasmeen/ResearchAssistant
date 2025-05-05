import os
import sys
from flask import Flask, request, jsonify, Blueprint
from flask_cors import CORS
import asyncio
from typing import Dict, Any
from functools import wraps

# Add the project root to the Python path to ensure package imports work correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

# Import all necessary modules
from research_assistant.retrieval.lit_review_engine import search_papers
from research_assistant.ranking.paper_ranker import rank_papers_by_relevance
from research_assistant.draft.generator import ResearchDraftGenerator
from research_assistant.draft.formatter import LaTeXFormatter
from research_assistant.draft.templates import ResearchTemplates

def async_route(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))
    return wrapped

# Create Blueprint for draft preparation routes
draft_bp = Blueprint('draft', __name__, url_prefix='/api/draft')

# Create Blueprint for search routes
search_bp = Blueprint('search', __name__, url_prefix='/api/search')

# Initialize components
generator = ResearchDraftGenerator()
formatter = LaTeXFormatter()

# Draft Blueprint routes
@draft_bp.route('/generate-titles', methods=['POST'])
@async_route
async def generate_titles():
    """Generate potential paper titles based on the research topic."""
    try:
        data = request.json
        research_topic = data.get('research_topic')
        count = data.get('count', 5)  # Default to 5 titles if not specified

        if not research_topic:
            return jsonify({
                'success': False,
                'error': 'Missing required field: research_topic'
            }), 400

        # Use the actual ResearchDraftGenerator to generate titles
        titles = await generator.generate_title_suggestions(
            research_topic=research_topic,
            count=count
        )

        return jsonify({
            'success': True,
            'titles': titles
        })

    except Exception as e:
        import traceback
        print(f"Title generation error: {e}")
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    

@draft_bp.route('/generate-outline', methods=['POST'])
@async_route
async def generate_outline():
    """Generate potential paper outline based on the research topic and paper type."""
    try:
        data = request.json
        research_topic = data.get('research_topic')
        paper_type = data.get('paper_type', 'standard')  # Default to 'standard' if not provided

        if not research_topic:
            return jsonify({
                'success': False,
                'error': 'Missing required field: research_topic'
            }), 400

        # Generate outline using the updated method
        outline = await generator.generate_outline(
            research_topic=research_topic,
            paper_type=paper_type
        )

        return jsonify({
            'success': True,
            'outline': outline
        })

    except Exception as e:
        import traceback
        print(f"Outline generation error: {e}")
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    
    
@draft_bp.route('/generate-section', methods=['POST'])
@async_route  # Add this decorator
async def generate_section():
    """Generate a specific section of a research paper."""
    try:
        data = request.json
        
        required_fields = ['research_topic', 'section_type']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        research_topic = data['research_topic']
        section_type = data['section_type']
        literature_summary = data.get('literature_summary', {})
        research_gaps = data.get('research_gaps', [])
        
        # Generate section content
        section_content = await generator.generate_section(
            research_topic=research_topic,
            section_type=section_type,
            literature_summary=literature_summary,
            research_gaps=research_gaps
        )
        
        return jsonify({
            'success': True,
            'section_type': section_type,
            'content': section_content
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Fix the generate_paper route
@draft_bp.route('/generate-paper', methods=['POST'])
@async_route  # Add this decorator
async def generate_paper():
    """Generate a complete research paper."""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['research_topic', 'paper_type']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Extract data
        research_topic = data['research_topic']
        paper_type = data['paper_type']
        literature_summary = data.get('literature_summary', {})
        research_gaps = data.get('research_gaps', [])
        
        # Get paper structure based on type
        structure = ResearchTemplates.get_paper_structure(paper_type)
        
        # Generate each section
        paper_sections = {}
        for section in structure:
            paper_sections[section] = await generator.generate_section(
                research_topic=research_topic,
                literature_summary=literature_summary,
                research_gaps=research_gaps,
                section_type=section
            )
        
        # Return all generated sections
        return jsonify({
            'success': True,
            'paper_type': paper_type,
            'sections': paper_sections
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Fix the refine_section route
@draft_bp.route('/refine-section', methods=['POST'])
@async_route  # Add this decorator
async def refine_section():
    """Refine a specific section based on feedback."""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['section_text', 'feedback']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Extract data
        section_text = data['section_text']
        feedback = data['feedback']
        
        # Refine section
        refined_section = await generator.refine_section(
            section_text=section_text,
            feedback=feedback
        )
        
        # Return refined content
        return jsonify({
            'success': True,
            'original': section_text,
            'refined': refined_section
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Search Blueprint routes
@search_bp.route('', methods=['POST'])
def search():
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
                "score": round(paper.get("relevance_score", 0), 2)
            })
        
        return jsonify({"results": simplified_results})
    
    except Exception as e:
        import traceback
        print(f"API error: {e}")
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": "*"}})  # Enable CORS for all routes
    
    # Register blueprints
    app.register_blueprint(draft_bp)
    app.register_blueprint(search_bp)
    
    return app

if __name__ == "__main__":
    app = create_app()
    print("Starting Research Assistant API server on http://localhost:5000")
    app.run(debug=True, port=5000)