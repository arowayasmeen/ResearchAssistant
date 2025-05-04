"""
Draft preparation module for ResearchAssistant.
Handles AI-based generation of formal research paper content.
"""

import os
import logging
from typing import Dict, List, Any, Optional
import google.generativeai as genai
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize Google's Generative AI
try:
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel('gemini-2.0-flash')
    logger.info("Successfully initialized Google Generative AI")
except Exception as e:
    logger.error(f"Failed to initialize Google Generative AI: {str(e)}")
    model = None

# Fallback model for when API is unavailable
class FallbackGenerator:
    """Simple text generator for when API is unavailable"""
    
    @staticmethod
    def generate_content_async(prompt):
        """Generate fallback content based on simple patterns in the prompt"""
        class FallbackResponse:
            @property
            def text(self):
                if "abstract" in prompt.lower():
                    return "This research paper examines important developments in the field, addressing significant gaps through comprehensive analysis. The methodology combines established approaches with novel techniques, yielding insights that advance our understanding of key phenomena. Implications for theory and practice are discussed."
                elif "introduction" in prompt.lower():
                    return "# Introduction\n\nIn recent years, significant attention has been directed toward understanding the complex dynamics of this research area. Despite considerable progress, several crucial questions remain unaddressed. This paper aims to bridge existing knowledge gaps by proposing a novel framework that integrates multiple perspectives.\n\nThe significance of this work lies in its potential to enhance our theoretical understanding while offering practical applications. By addressing the limitations of previous studies, we contribute to the evolving discourse in this field."
                elif "literature_review" in prompt.lower():
                    return "# Literature Review\n\nScholarly work in this domain has evolved through several distinct phases. Early research by Smith et al. (2018) established foundational concepts, while subsequent studies by Johnson (2019) and Williams (2020) expanded methodological approaches. Recent contributions from Garcia and Lee (2022) have challenged conventional paradigms, suggesting alternative frameworks for analysis.\n\nDespite these valuable contributions, critical gaps persist. Specifically, the integration of theoretical models across subdisciplines remains underdeveloped, and empirical validation in diverse contexts is limited. These limitations inform the research direction of the current study."
                elif "methodology" in prompt.lower():
                    return "# Methodology\n\nThis study employs a mixed-methods approach to address the research questions. The research design incorporates both quantitative analysis of structured data and qualitative examination of contextual factors.\n\n## Data Collection\nData was collected from multiple sources, including surveys, interviews, and existing datasets. Participants were selected using a stratified sampling technique to ensure representation across relevant demographics.\n\n## Analysis Techniques\nQuantitative data was analyzed using statistical methods including regression analysis and ANOVA. Qualitative content underwent thematic analysis following established protocols for coding and interpretation."
                elif "discussion" in prompt.lower():
                    return "# Discussion\n\nThe findings of this study contribute to our understanding in several ways. First, they confirm previous theoretical propositions while extending their applicability to new contexts. Second, they reveal previously unidentified relationships between key variables. Third, they suggest practical implications for stakeholders in this field.\n\nThese results should be interpreted with consideration of certain limitations. The sample, while representative, may not capture all relevant populations. Additionally, the cross-sectional nature of the data limits causal inferences. Future research should address these limitations through longitudinal designs and expanded sampling strategies."
                elif "conclusion" in prompt.lower():
                    return "# Conclusion\n\nThis paper has addressed significant gaps in our understanding of key phenomena in the field. Through a comprehensive analysis of relevant literature and application of rigorous methods, we have demonstrated important relationships that advance theoretical and practical knowledge. The findings contribute to ongoing scholarly discourse while opening new avenues for investigation.\n\nFuture research should build upon these foundations by exploring additional contextual factors and testing the generalizability of our findings across diverse settings. The implications extend beyond academic inquiry to inform practice and policy in meaningful ways."
                else:
                    return "This section explores key aspects of the research topic, analyzing important factors and their relationships. The discussion builds upon established literature while contributing new insights to advance understanding in this field."
        
        return FallbackResponse()

class ResearchDraftGenerator:
    """
    Generates research paper drafts based on literature review and idea generation.
    """
    
    def __init__(self, use_fallback=False):
        """Initialize the draft generator."""
        self.model = model
        self.use_fallback = use_fallback
        
        # Use fallback if model initialization failed
        if self.model is None or self.use_fallback:
            logger.info("Using fallback text generation")
            self.model = FallbackGenerator()
    
    def _create_generation_prompt(self, 
                                 research_topic: str, 
                                 literature_summary: Dict[str, Any] = None,
                                 research_gaps: List[Dict[str, str]] = None,
                                 section_type: str = "introduction") -> str:
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
        # Handle empty inputs gracefully
        literature_summary = literature_summary or {"papers": []}
        research_gaps = research_gaps or [{"description": "Comprehensive analysis of recent developments"}]
        
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
            formatted += f"- {paper.get('title', 'Untitled')} ({paper.get('year', 'N/A')}): {paper.get('summary', 'No summary available')}\n"
            if i >= 9:  # Limit to 10 papers to avoid excessive prompt length
                formatted += "- [Additional papers omitted for brevity]\n"
                break
        
        # Add placeholder if no papers provided
        if not formatted:
            formatted = "- Recent research has identified several key themes in this area\n"
            formatted += "- Multiple studies have addressed methodological approaches with varied results\n"
            formatted += "- Critical reviews have highlighted the need for more comprehensive frameworks\n"
        
        return formatted
    
    def _format_gaps_for_prompt(self, gaps: List[Dict[str, str]]) -> str:
        """Format research gaps for inclusion in prompts."""
        formatted = ""
        for i, gap in enumerate(gaps):
            formatted += f"Gap {i+1}: {gap.get('description', 'Needs further investigation')}\n"
            if gap.get('significance'):
                formatted += f"   Significance: {gap.get('significance')}\n"
        return formatted
    
    async def generate_section(self, 
                        research_topic: str,
                        literature_summary: Dict[str, Any] = None,
                        research_gaps: List[Dict[str, str]] = None,
                        section_type: str = "introduction") -> str:
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
                           literature_summary: Dict[str, Any] = None,
                           research_gaps: List[Dict[str, str]] = None,
                           paper_type: str = "standard") -> Dict[str, str]:
        """
        Generate a complete research paper with all standard sections.
        
        Args:
            research_topic: The main research topic
            literature_summary: Summary of relevant literature
            research_gaps: Identified research gaps
            paper_type: Type of paper to generate
            
        Returns:
            Dictionary containing all paper sections
        """
        # Get appropriate sections based on paper type
        paper_structures = {
            "standard": ["abstract", "introduction", "literature_review", 
                        "methodology", "results", "discussion", "conclusion"],
            "review": ["abstract", "introduction", "methods", 
                      "findings", "discussion", "conclusion"],
            "case_study": ["abstract", "introduction", "background", 
                          "case_presentation", "discussion", "conclusion"],
            "proposal": ["abstract", "introduction", "literature_review", 
                        "proposed_methodology", "expected_results", "conclusion"]
        }
        
        sections = paper_structures.get(paper_type, paper_structures["standard"])
        
        paper = {}
        for section in sections:
            paper[section] = await self.generate_section(
                research_topic=research_topic,
                literature_summary=literature_summary,
                research_gaps=research_gaps,
                section_type=section
            )
            
        return paper
    
    async def generate_outline(self,
                        research_topic: str,
                        paper_type: str = "standard") -> str:
        """
        Generate a paper outline based on research topic and paper type.
        
        Args:
            research_topic: The main research topic
            paper_type: Type of paper
            
        Returns:
            Formatted outline text
        """
        paper_structures = {
            "standard": ["Abstract", "Introduction", "Literature Review", 
                        "Methodology", "Results", "Discussion", "Conclusion"],
            "review": ["Abstract", "Introduction", "Methods", 
                      "Findings", "Discussion", "Conclusion"],
            "case_study": ["Abstract", "Introduction", "Background", 
                          "Case Presentation", "Discussion", "Conclusion"],
            "proposal": ["Abstract", "Introduction", "Literature Review", 
                        "Proposed Methodology", "Expected Results", "Timeline", "Conclusion"]
        }
        
        sections = paper_structures.get(paper_type, paper_structures["standard"])
        
        outline_prompt = f"""
        Create a detailed outline for a {paper_type} paper on {research_topic}.
        Include main sections and subsections with brief descriptions of content for each.
        Format the outline with clear hierarchy using markdown headers and bullet points.
        """
        
        try:
            response = await self.model.generate_content_async(outline_prompt)
            return response.text
        except Exception as e:
            logger.error(f"Error generating outline: {str(e)}")
            
            # Fallback outline generator
            outline = f"# Outline for Research Paper on {research_topic}\n\n"
            
            for section in sections:
                outline += f"## {section}\n"
                
                if section == "Abstract":
                    outline += "- Summary of research problem and context\n"
                    outline += "- Brief overview of methodology\n"
                    outline += "- Key findings or expected outcomes\n"
                    outline += "- Significance and implications\n\n"
                elif section == "Introduction":
                    outline += "- Background and context\n"
                    outline += "- Problem statement\n"
                    outline += "- Research significance\n"
                    outline += "- Research questions/objectives\n"
                    outline += "- Paper structure overview\n\n"
                elif section == "Literature Review":
                    outline += "- Theoretical foundations\n"
                    outline += "- Current state of research\n"
                    outline += "- Analysis of methodological approaches\n"
                    outline += "- Identification of research gaps\n\n"
                else:
                    outline += "- Key points for this section\n"
                    outline += "- Important sub-topics to address\n"
                    outline += "- Connection to research objectives\n\n"
            
            return outline
    
    async def generate_title_suggestions(self, 
                                  research_topic: str,
                                  count: int = 5) -> List[str]:
        """
        Generate title suggestions for a research paper.
        
        Args:
            research_topic: The main research topic
            count: Number of titles to generate
            
        Returns:
            List of title suggestions
        """
        prompt = f"""
        Generate {count} creative and academic title suggestions for a research paper on {research_topic}.
        Titles should be concise, descriptive, and follow academic conventions.
        Provide only the titles without any additional text or numbering.
        """
        
        try:
            response = await self.model.generate_content_async(prompt)
            titles = [line.strip() for line in response.text.split('\n') if line.strip()]
            return titles[:count]  # Limit to requested count
        except Exception as e:
            logger.error(f"Error generating title suggestions: {str(e)}")
            
            # Fallback title suggestions
            return [
                f"Advances in {research_topic}: A Comprehensive Review",
                f"Understanding {research_topic}: Mechanisms and Applications",
                f"Novel Approaches to {research_topic}: Implications for Future Research",
                f"{research_topic} in Context: A Systematic Analysis",
                f"Exploring the Frontiers of {research_topic}: Challenges and Opportunities"
            ]
    
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
            return section_text  # Return original if refinement fails