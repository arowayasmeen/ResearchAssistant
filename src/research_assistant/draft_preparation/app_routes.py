from flask import Blueprint, request, jsonify
import asyncio
from typing import Dict, Any

from research_assistant.draft_preparation.generator import ResearchDraftGenerator
from research_assistant.draft_preparation.formatter import LaTeXFormatter
from research_assistant.draft_preparation.templates import ResearchTemplates

# Create Blueprint for draft preparation routes
draft_bp = Blueprint('draft', __name__, url_prefix='/api/draft')

# Initialize components
generator = ResearchDraftGenerator()
formatter = LaTeXFormatter()

@draft_bp.route('/generate-section', methods=['POST'])
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

@draft_bp.route('/generate-paper', methods=['POST'])
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

@draft_bp.route('/format-latex', methods=['POST'])
def format_latex():
    """Convert paper content to LaTeX format."""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['paper_data', 'metadata']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Extract data
        paper_data = data['paper_data']
        metadata = data['metadata']
        literature = data.get('literature', [])
        template_type = metadata.get('template_type', 'article')
        
        # Initialize formatter with template type
        formatter = LaTeXFormatter(template_type=template_type)
        
        # Generate LaTeX document
        latex_document = formatter.create_complete_document(
            paper_data=paper_data,
            metadata=metadata,
            literature=literature
        )
        
        # Generate bibliography
        bibliography = formatter.generate_bibliography()
        
        # Return LaTeX content
        return jsonify({
            'success': True,
            'latex': latex_document,
            'bibliography': bibliography
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@draft_bp.route('/refine-section', methods=['POST'])
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

# Function to register all draft routes with the main app
def register_draft_routes(app):
    """Register draft preparation routes with the Flask app."""
    app.register_blueprint(draft_bp)
    return app