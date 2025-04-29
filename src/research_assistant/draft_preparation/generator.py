"""
Draft preparation module for ResearchAssistant.
Handles AI-based generation of formal research paper content.
"""

import os
import logging
from typing import Dict, List, Any, Optional
import google.generativeai as genai
from dotenv import load_dotenv
#from research_assistant.utils.embedding import get_embeddings
#from research_assistant.retrieval.literature import get_relevant_literature

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize Google's Generative AI
try:
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    evaluation_model = genai.GenerativeModel('gemini')
    logger.info("Successfully initialized Google Generative AI")
except Exception as e:
    logger.error(f"Failed to initialize Google Generative AI: {str(e)}")
    model = None

class ResearchDraftGenerator:
    """
    Generates research paper drafts based on literature review and idea generation.
    """
    
    def __init__(self):
        """Initialize the draft generator."""
        self.model = model
        
    def _create_generation_prompt(self, 
                                 research_topic: str, 
                                 literature_summary: Dict[str, Any],
                                 research_gaps: List[Dict[str, str]],
                                 section_type: str) -> str:
        """
        Create a specialized prompt for generating specific research paper sections.
        
        Args:
            research_topic: The main research topic
            literature_summary: Summary of relevant literature
            research_gaps: Identified research gaps
            section_type: Type of section to generate (abstract, intro, etc.)
            
        Returns:
            A formatted prompt string
        """
        # Base context for all sections
        base_context = f"""
        You are an expert academic writer creating a formal research paper on: {research_topic}.
        
        The paper should be written in a formal academic style with proper citations.
        Maintain objectivity and precise language throughout.
        Use appropriate academic terminology while ensuring clarity.
        
        Key literature summary:
        {self._format_literature_for_prompt(literature_summary)}
        
        Identified research gaps:
        {self._format_gaps_for_prompt(research_gaps)}
        """
        
        # Section-specific prompts
        section_prompts = {
            "abstract": f"{base_context}\n\nWrite a compelling abstract (150-250 words) that summarizes the research problem, methodology, and significance of addressing the identified gaps.",
            
            "introduction": f"{base_context}\n\nWrite an introduction that establishes the research context, highlights the importance of the area, introduces the identified gaps, and outlines the paper's contribution. Use 3-5 paragraphs with logical flow.",
            
            "literature_review": f"{base_context}\n\nWrite a comprehensive literature review that synthesizes and critically analyzes the existing research, organized thematically. Highlight connections between studies and identify trends and limitations.",
            
            "methodology": f"{base_context}\n\nDevelop a methodology section that outlines a research approach to address the identified gaps. Include specific methods, data collection procedures, and analysis techniques appropriate for this research area.",
            
            "discussion": f"{base_context}\n\nWrite a discussion section that interprets potential findings in relation to the existing literature, addresses limitations, and suggests future research directions.",
            
            "conclusion": f"{base_context}\n\nWrite a concise conclusion that reiterates the research problem, summarizes contributions, and emphasizes the significance of addressing the identified gaps."
        }
        
        return section_prompts.get(section_type, base_context)
    
    def _format_literature_for_prompt(self, literature_summary: Dict[str, Any]) -> str:
        """Format literature summary for inclusion in prompts."""
        formatted = ""
        for i, paper in enumerate(literature_summary.get('papers', [])):
            formatted += f"- {paper.get('title')} ({paper.get('year')}): {paper.get('summary')}\n"
            if i >= 9:  # Limit to 10 papers to avoid excessive prompt length
                formatted += "- [Additional papers omitted for brevity]\n"
                break
        return formatted
    
    def _format_gaps_for_prompt(self, gaps: List[Dict[str, str]]) -> str:
        """Format research gaps for inclusion in prompts."""
        formatted = ""
        for i, gap in enumerate(gaps):
            formatted += f"Gap {i+1}: {gap.get('description')}\n"
            if gap.get('significance'):
                formatted += f"   Significance: {gap.get('significance')}\n"
        return formatted
    
    async def generate_section(self, 
                        research_topic: str,
                        literature_summary: Dict[str, Any],
                        research_gaps: List[Dict[str, str]],
                        section_type: str) -> str:
        """
        Generate a specific section of a research paper.
        
        Args:
            research_topic: The main research topic
            literature_summary: Summary of relevant literature
            research_gaps: Identified research gaps
            section_type: Type of section to generate
            
        Returns:
            Generated text for the requested section
        """
        if not self.model:
            logger.error("Generative AI model not initialized")
            return "Error: Text generation model not available."
            
        prompt = self._create_generation_prompt(
            research_topic=research_topic,
            literature_summary=literature_summary,
            research_gaps=research_gaps,
            section_type=section_type
        )
        
        try:
            logger.info(f"Generating {section_type} section")
            response = await self.model.generate_content_async(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Error generating {section_type}: {str(e)}")
            return f"Error generating {section_type}. Please try again."
    
    async def generate_full_paper(self,
                           research_topic: str,
                           literature_summary: Dict[str, Any],
                           research_gaps: List[Dict[str, str]]) -> Dict[str, str]:
        """
        Generate a complete research paper with all standard sections.
        
        Args:
            research_topic: The main research topic
            literature_summary: Summary of relevant literature
            research_gaps: Identified research gaps
            
        Returns:
            Dictionary containing all paper sections
        """
        sections = ["abstract", "introduction", "literature_review", 
                   "methodology", "discussion", "conclusion"]
        
        paper = {}
        for section in sections:
            paper[section] = await self.generate_section(
                research_topic=research_topic,
                literature_summary=literature_summary,
                research_gaps=research_gaps,
                section_type=section
            )
            
        return paper
    
    async def refine_section(self,
                      section_text: str,
                      feedback: str) -> str:
        """
        Refine a section based on feedback.
        
        Args:
            section_text: Original section text
            feedback: Specific feedback to address
            
        Returns:
            Refined section text
        """
        if not self.model:
            return "Error: Text generation model not available."
            
        refine_prompt = f"""
        You are an expert academic editor. Revise the following research paper section 
        based on this specific feedback:
        
        FEEDBACK:
        {feedback}
        
        ORIGINAL TEXT:
        {section_text}
        
        Provide a revised version that addresses the feedback while maintaining 
        academic style and improving overall quality.
        """
        
        try:
            response = await self.model.generate_content_async(refine_prompt)
            return response.text
        except Exception as e:
            logger.error(f"Error refining section: {str(e)}")
            return "Error refining section. Please try again."