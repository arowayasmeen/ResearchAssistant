from typing import Dict, List, Any, Optional
import google.generativeai as genai
import logging
import os

logger = logging.getLogger(__name__)

class ResearchTemplates:
    """Contains templates for different types of research papers."""
    
    @staticmethod
    def get_paper_structure(paper_type: str) -> List[str]:
        """
        Get the structure (sections) for a specific paper type.
        
        Args:
            paper_type (str): The type of paper (standard, review, etc.)
            
        Returns:
            List[str]: List of section names for the paper type
        """
        structures = {
            "standard": [
                "abstract", 
                "introduction", 
                "literature_review", 
                "methodology", 
                "results", 
                "discussion", 
                "conclusion", 
                "references"
            ],
            "review": [
                "abstract", 
                "introduction", 
                "methods", 
                "findings", 
                "discussion", 
                "implications", 
                "conclusion", 
                "references"
            ],
            "case_study": [
                "abstract", 
                "introduction", 
                "background", 
                "case_presentation", 
                "analysis", 
                "discussion", 
                "conclusion", 
                "references"
            ],
            "experimental": [
                "abstract", 
                "introduction", 
                "materials_and_methods", 
                "experimental_setup", 
                "results", 
                "analysis", 
                "discussion", 
                "conclusion", 
                "references"
            ]
        }
        
        return structures.get(paper_type.lower(), structures["standard"])


class ResearchDraftGenerator:
    """
    A class that generates research paper drafts using Google's GenerativeAI.
    """
    
    def __init__(self):
        """Initialize the generator with the Gemini model."""
        try:
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("Google API key not found in environment variables")
                
            # Configure the client
            genai.configure(api_key=api_key)
            
            # Initialize the model
            self.model = genai.GenerativeModel('gemini-2.0-flash')
            logger.info("Successfully initialized Google Generative AI model")
        except Exception as e:
            logger.error(f"Failed to initialize Google Generative AI: {str(e)}")
            self.model = None
    
    async def generate_title_suggestions(self, research_topic: str, count: int = 5) -> List[str]:
        """
        Generate title suggestions for a research paper.
        
        Args:
            research_topic (str): The main research topic
            count (int): Number of title suggestions to generate
            
        Returns:
            List[str]: List of title suggestions
        """
        if not self.model:
            raise ValueError("AI model not initialized")
            
        prompt = f"""
        Generate {count} potential academic titles for a research paper on the topic: {research_topic}.
        The titles should be concise, academic, and capture attention while accurately representing the research focus.
        Format your response as a numbered list with just the titles.
        """
        
        try:
            response = await self.model.generate_content_async(prompt)
            
            # Extract titles from the response
            text = response.text
            
            # Parse the numbered list
            titles = []
            for line in text.split('\n'):
                line = line.strip()
                if line and (line[0].isdigit() or line[0] == '-'):
                    # Remove the number/bullet and any leading characters
                    title = line.lstrip('0123456789.- ').strip()
                    if title:
                        titles.append(title)
            
            # Ensure we return the requested number of titles if possible
            return titles[:count]
        except Exception as e:
            logger.error(f"Error generating title suggestions: {str(e)}")
            raise
    
    async def generate_outline(self, research_topic: str, paper_type: str = "standard") -> str:
        """
        Generate a research paper outline based on the topic and paper type.
        
        Args:
            research_topic (str): The main research topic
            paper_type (str): Type of paper (standard, review, etc.)
            
        Returns:
            str: A formatted outline in markdown format
        """
        if not self.model:
            raise ValueError("AI model not initialized")
            
        # Get the appropriate paper structure based on the paper type
        paper_sections = ResearchTemplates.get_paper_structure(paper_type)
        
        # Create a prompt that specifies the sections we want
        prompt = f"""
        Create a detailed outline for a research paper on "{research_topic}".
        
        The paper should follow the structure of a {paper_type} research paper with these sections:
        {', '.join(section.replace('_', ' ').title() for section in paper_sections)}
        
        For each section, provide:
        1. A brief description of what should be included
        2. 3-5 key points or subsections
        
        Format the outline in markdown with:
        - Main sections as level 2 headers (##)
        - Subsections as bullet points
        - Brief descriptions as normal text
        
        The outline should be comprehensive yet concise, guiding the research paper writing process.
        """
        
        try:
            response = await self.model.generate_content_async(prompt)
            
            # Return the outline as markdown text
            return response.text
        except Exception as e:
            logger.error(f"Error generating outline: {str(e)}")
            raise
    
    async def generate_section(
        self, 
        research_topic: str, 
        section_type: str,
        literature_summary: Optional[Dict[str, Any]] = None,
        research_gaps: Optional[List[str]] = None
    ) -> str:
        """
        Generate content for a specific section of a research paper.
        
        Args:
            research_topic (str): The main research topic
            section_type (str): The type of section to generate (e.g., 'introduction')
            literature_summary (Dict, optional): Summary of literature review findings
            research_gaps (List[str], optional): List of identified research gaps
            
        Returns:
            str: The generated section content
        """
        if not self.model:
            raise ValueError("AI model not initialized")
            
        # Format the section name for display
        section_name = section_type.replace('_', ' ').title()
        
        # Create a base prompt for the section
        prompt = f"""
        Write a {section_name} section for a research paper on "{research_topic}".
        
        The section should be well-structured, academically rigorous, and appropriate for a scholarly publication.
        """
        
        # Add specific guidance based on the section type
        if section_type == "abstract":
            prompt += """
            The abstract should:
            - Provide a concise summary of the paper (150-250 words)
            - Include the research problem, methodology, key findings, and implications
            - Be self-contained and understandable without reading the full paper
            """
        elif section_type == "introduction":
            prompt += """
            The introduction should:
            - Clearly state the research problem and its significance
            - Provide necessary background information
            - Present the research questions or hypotheses
            - Outline the paper's structure
            """
        elif section_type == "literature_review":
            prompt += """
            The literature review should:
            - Summarize and synthesize relevant prior research
            - Identify patterns, gaps, and controversies in the literature
            - Establish the theoretical framework
            - Justify the need for the current study
            """
            
            # Add literature summary if provided
            if literature_summary:
                prompt += f"\nIncorporate these key findings from the literature:\n"
                for source, findings in literature_summary.items():
                    prompt += f"- {source}: {findings}\n"
        
        elif section_type == "methodology":
            prompt += """
            The methodology section should:
            - Describe the research design in detail
            - Explain methods for data collection and analysis
            - Justify methodological choices
            - Address limitations and ethical considerations
            """
        elif section_type == "results":
            prompt += """
            The results section should:
            - Present findings without interpretation
            - Use clear, organized structures (tables, figures, etc.)
            - Highlight key patterns and relationships in the data
            - Address each research question or hypothesis
            """
        elif section_type == "discussion":
            prompt += """
            The discussion section should:
            - Interpret the results in context of the research questions
            - Connect findings to existing literature
            - Address limitations and alternative explanations
            - Propose implications for theory and practice
            """
            
            # Add research gaps if provided
            if research_gaps:
                prompt += f"\nAddress these research gaps in your discussion:\n"
                for gap in research_gaps:
                    prompt += f"- {gap}\n"
                    
        elif section_type == "conclusion":
            prompt += """
            The conclusion should:
            - Summarize the key findings
            - Emphasize the significance and implications
            - Suggest directions for future research
            - End with a compelling closing statement
            """
        elif section_type == "references":
            prompt += """
            Create a list of 10-15 fictional but realistic academic references related to this topic.
            Format them in APA style.
            Include a mix of journal articles, books, and conference proceedings.
            Use realistic author names, publication years (within the last 20 years), and titles.
            """
            
        # Add a final instruction for formatting
        prompt += """
        
        Format the section with appropriate headings, paragraphs, and academic language.
        The content should be 500-800 words and ready to be included in a research paper.
        """
        
        try:
            response = await self.model.generate_content_async(prompt)
            
            # Return the generated section content
            return response.text
        except Exception as e:
            logger.error(f"Error generating {section_type} section: {str(e)}")
            raise
    
    async def refine_section(self, section_text: str, feedback: str) -> str:
        """
        Refine a section based on feedback.
        
        Args:
            section_text (str): The original section text
            feedback (str): Feedback for improvement
            
        Returns:
            str: The refined section text
        """
        if not self.model:
            raise ValueError("AI model not initialized")
            
        prompt = f"""
        Revise and improve the following research paper section based on this feedback:
        
        FEEDBACK:
        {feedback}
        
        ORIGINAL SECTION:
        {section_text}
        
        Please provide a revised version that addresses the feedback while maintaining academic rigor and appropriate structure.
        The revised section should be well-organized, clearly written, and ready for inclusion in a scholarly paper.
        """
        
        try:
            response = await self.model.generate_content_async(prompt)
            
            # Return the refined section
            return response.text
        except Exception as e:
            logger.error(f"Error refining section: {str(e)}")
            raise