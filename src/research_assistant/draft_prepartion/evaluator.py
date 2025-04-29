"""
Quality assessment for research paper drafts.
Provides automated evaluation and improvement suggestions.
"""

import re
import logging
from typing import Dict, List, Any, Tuple
import google.generativeai as genai
from dotenv import load_dotenv
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize Google's Generative AI
try:
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    evaluation_model = genai.GenerativeModel('gemini-pro')
    logger.info("Successfully initialized evaluation model")
except Exception as e:
    logger.error(f"Failed to initialize evaluation model: {str(e)}")
    evaluation_model = None

class DraftEvaluator:
    """
    Evaluates and provides improvement suggestions for research paper drafts.
    """
    
    def __init__(self):
        """Initialize the draft evaluator."""
        self.model = evaluation_model
        
    async def evaluate_section(self, 
                        section_type: str, 
                        content: str,
                        evaluation_criteria: List[str] = None) -> Dict[str, Any]:
        """
        Evaluate a specific section of a research paper.
        
        Args:
            section_type: Type of section (abstract, introduction, etc.)
            content: Section content
            evaluation_criteria: Specific criteria to evaluate against
            
        Returns:
            Evaluation results with scores and suggestions
        """
        if not self.model:
            logger.error("Evaluation model not initialized")
            return {"error": "Evaluation model not available"}
        
        # Default evaluation criteria if none provided
        if not evaluation_criteria:
            evaluation_criteria = self._get_default_criteria(section_type)
        
        # Create evaluation prompt
        prompt = self._create_evaluation_prompt(section_type, content, evaluation_criteria)
        
        try:
            # Generate evaluation
            response = await self.model.generate_content_async(prompt)
            evaluation_text = response.text
            
            # Parse evaluation results
            scores, suggestions = self._parse_evaluation_results(evaluation_text)
            
            return {
                "section": section_type,
                "scores": scores,
                "suggestions": suggestions,
                "overall_score": sum(scores.values()) / len(scores) if scores else 0
            }
        except Exception as e:
            logger.error(f"Error evaluating {section_type}: {str(e)}")
            return {"error": f"Error evaluating section: {str(e)}"}
    
    def _get_default_criteria(self, section_type: str) -> List[str]:
        """
        Get default evaluation criteria for a specific section type.
        
        Args:
            section_type: Type of section
            
        Returns:
            List of evaluation criteria
        """
        # Common criteria for all sections
        common_criteria = [
            "Clarity and conciseness",
            "Logical flow and organization",
            "Academic language and tone",
            "Technical accuracy",
            "Citation quality and integration"
        ]
        
        # Section-specific criteria
        specific_criteria = {
            "abstract": [
                "Completeness (includes problem, method, results, significance)",
                "Self-contained nature",
                "Adheres to word limit (150-250 words)"
            ],
            "introduction": [
                "Clear problem statement",
                "Research gap identification",
                "Research significance justification",
                "Paper structure overview"
            ],
            "literature_review": [
                "Comprehensive coverage of relevant literature",
                "Critical analysis (not just summary)",
                "Thematic organization",
                "Clear connection to research gap"
            ],
            "methodology": [
                "Appropriateness of methods for research questions",
                "Clear description of procedures",
                "Consideration of limitations",
                "Replicability of methods"
            ],
            "discussion": [
                "Interpretation linked to results",
                "Connection to existing literature",
                "Discussion of limitations",
                "Future research directions"
            ],
            "conclusion": [
                "Summary of key findings",
                "Research contribution emphasis",
                "No new information introduced",
                "Compelling closing"
            ]
        }
        
        # Combine common criteria with section-specific criteria
        return common_criteria + specific_criteria.get(section_type, [])
    
    def _create_evaluation_prompt(self, 
                                section_type: str, 
                                content: str,
                                criteria: List[str]) -> str:
        """
        Create a prompt for evaluating a research paper section.
        
        Args:
            section_type: Type of section
            content: Section content
            criteria: Evaluation criteria
            
        Returns:
            Evaluation prompt
        """
        criteria_text = "\n".join([f"- {c}" for c in criteria])
        
        return f"""
        You are an expert academic editor evaluating a {section_type} section of a research paper.
        
        Please evaluate the following {section_type} based on these criteria:
        {criteria_text}
        
        SECTION CONTENT:
        {content}
        
        Please provide:
        1. A numerical score (1-10) for each criterion
        2. Specific suggestions for improvement for each criterion
        3. Examples of problematic sentences/paragraphs and how to fix them
        
        Format your response as follows:
        
        EVALUATION:
        [Criterion 1]: [Score]/10
        - [Specific suggestion]
        - [Example problem]: "[Problematic text]"
        - [Example solution]: "[Improved text]"
        
        [Criterion 2]: [Score]/10
        ...and so on for each criterion.
        
        OVERALL ASSESSMENT:
        [Brief summary of strengths and major improvement areas]
        """
    
    def _parse_evaluation_results(self, evaluation_text: str) -> Tuple[Dict[str, float], Dict[str, List[str]]]:
        """
        Parse evaluation results from the model's response.
        
        Args:
            evaluation_text: Raw evaluation text
            
        Returns:
            Tuple of (scores_dict, suggestions_dict)
        """
        scores = {}
        suggestions = {}
        
        # Simple regex pattern to extract criterion scores
        # Format: [Criterion]: [Score]/10
        score_pattern = r'([^:]+): (\d+(?:\.\d+)?)/10'
        
        # Find all score matches
        score_matches = re.findall(score_pattern, evaluation_text)
        for criterion, score in score_matches:
            criterion = criterion.strip()
            scores[criterion] = float(score)
            
            # Find suggestions for this criterion
            criterion_start = evaluation_text.find(f"{criterion}:")
            if criterion_start >= 0:
                next_criterion = evaluation_text.find(":", criterion_start + len(criterion) + 1)
                if next_criterion < 0:
                    next_criterion = len(evaluation_text)
                    
                criterion_text = evaluation_text[criterion_start:next_criterion]
                # Extract bullet points (lines starting with - or •)
                suggestion_lines = re.findall(r'[-•]\s+([^\n]+)', criterion_text)
                suggestions[criterion] = suggestion_lines
        
        return scores, suggestions
    
    async def evaluate_full_paper(self, paper: Dict[str, str]) -> Dict[str, Any]:
        """
        Evaluate all sections of a research paper.
        
        Args:
            paper: Dictionary with section names as keys and content as values
            
        Returns:
            Dictionary with evaluation results for each section
        """
        results = {}
        overall_scores = []
        
        for section, content in paper.items():
            # Skip empty sections
            if not content or not content.strip():
                continue
                
            # Evaluate section
            section_eval = await self.evaluate_section(section, content)
            results[section] = section_eval
            
            # Collect overall score if available
            if "overall_score" in section_eval and isinstance(section_eval["overall_score"], (int, float)):
                overall_scores.append(section_eval["overall_score"])
        
        # Calculate paper-wide score
        paper_score = sum(overall_scores) / len(overall_scores) if overall_scores else 0
        
        return {
            "sections": results,
            "overall_score": paper_score,
            "recommendation": self._get_recommendation(paper_score)
        }
    
    def _get_recommendation(self, score: float) -> str:
        """
        Get an overall recommendation based on paper score.
        
        Args:
            score: Overall paper score
            
        Returns:
            Recommendation string
        """
        if score >= 9.0:
            return "Excellent quality paper. Minor revisions only."
        elif score >= 8.0:
            return "Strong paper. Some specific areas need improvement."
        elif score >= 7.0:
            return "Good foundation. Several areas need significant improvement."
        elif score >= 6.0:
            return "Acceptable draft. Multiple sections need substantial revision."
        else:
            return "Early draft stage. Comprehensive revision recommended."
            
    async def improve_writing_style(self, content: str, style_target: str = "academic") -> str:
        """
        Improve the writing style of content based on target style.
        
        Args:
            content: Text content to improve
            style_target: Target writing style
            
        Returns:
            Improved content
        """
        if not self.model:
            return content
            
        style_descriptions = {
            "academic": "formal academic writing with precise terminology, objective tone, and proper citations",
            "technical": "detailed technical writing with specific terminology, clear explanations, and systematic structure",
            "persuasive": "compelling writing that presents strong arguments, evidence, and rhetorical techniques",
            "concise": "clear, efficient writing that conveys information with minimal words"
        }
        
        style_desc = style_descriptions.get(style_target, style_descriptions["academic"])
        
        prompt = f"""
        Revise the following text to improve the writing style. 
        
        Target style: {style_desc}
        
        ORIGINAL TEXT:
        {content}
        
        Please maintain all technical information and key points while enhancing the style.
        Provide the revised version only, without explanations or comments.
        """
        
        try:
            response = await self.model.generate_content_async(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Error improving writing style: {str(e)}")
            return content
            
    async def check_citations(self, content: str, literature: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Check if citations are used properly and identify missing citations.
        
        Args:
            content: Text content to check
            literature: List of literature items
            
        Returns:
            Dictionary with citation analysis
        """
        if not self.model:
            return {"error": "Citation checking model not available"}
            
        # Extract author names from literature
        authors = []
        for item in literature:
            if 'authors' in item:
                author_list = item['authors'].split(',')
                for author in author_list:
                    last_name = author.strip().split()[-1]
                    authors.append(last_name)
        
        prompt = f"""
        Analyze the following text for citation quality and completeness.
        
        TEXT:
        {content}
        
        Known authors in the field: {', '.join(authors)}
        
        Please identify:
        1. Statements that need citations but currently lack them
        2. Incorrect or improperly formatted citations
        3. Overreliance on specific sources
        4. Missing relevant sources that should be cited
        
        Format your response as:
        
        MISSING CITATIONS:
        - [Statement that needs citation]
        
        IMPROPER CITATIONS:
        - [Current citation] -> [Suggested correction]
        
        CITATION BALANCE:
        - [Assessment of citation distribution]
        
        SUGGESTED ADDITIONAL SOURCES:
        - [Research area where additional citations would strengthen the paper]
        """
        
        try:
            response = await self.model.generate_content_async(prompt)
            analysis_text = response.text
            
            # Parse the response into structured data
            sections = {}
            current_section = None
            
            for line in analysis_text.split('\n'):
                line = line.strip()
                if not line:
                    continue
                    
                if line.endswith(':') and line.isupper():
                    current_section = line[:-1].title()
                    sections[current_section] = []
                elif current_section and line.startswith('-'):
                    sections[current_section].append(line[1:].strip())
            
            return {
                "analysis": sections,
                "has_issues": any(len(items) > 0 for items in sections.values())
            }
        except Exception as e:
            logger.error(f"Error checking citations: {str(e)}")
            return {"error": f"Error checking citations: {str(e)}"}