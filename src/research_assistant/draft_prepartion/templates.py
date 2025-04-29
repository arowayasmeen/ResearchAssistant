"""
Templates for generating different types of research papers.
"""

from typing import Dict, Any, List

class ResearchTemplates:
    """
    Provides templates for different types of research papers and sections.
    """
    
    @staticmethod
    def get_paper_structure(paper_type: str) -> List[str]:
        """
        Get the structure (sections) for a given paper type.
        
        Args:
            paper_type: Type of research paper
            
        Returns:
            List of section names
        """
        structures = {
            "standard": [
                "abstract", 
                "introduction", 
                "literature_review", 
                "methodology", 
                "results", 
                "discussion", 
                "conclusion"
            ],
            "review": [
                "abstract",
                "introduction",
                "methods",
                "findings",
                "discussion",
                "conclusion"
            ],
            "case_study": [
                "abstract",
                "introduction",
                "background",
                "case_presentation",
                "discussion",
                "conclusion"
            ],
            "proposal": [
                "abstract",
                "introduction",
                "literature_review",
                "proposed_methodology",
                "expected_results",
                "timeline",
                "conclusion"
            ]
        }
        
        return structures.get(paper_type, structures["standard"])
    
    @staticmethod
    def get_section_guidelines(section_name: str) -> Dict[str, Any]:
        """
        Get guidelines for writing a specific section.
        
        Args:
            section_name: Name of the section
            
        Returns:
            Dictionary with guidelines for the section
        """
        guidelines = {
            "abstract": {
                "word_count": "150-250",
                "components": [
                    "Research problem/question",
                    "Methodology overview",
                    "Key findings or expected contributions",
                    "Significance statement"
                ],
                "style": "Concise, clear, and self-contained"
            },
            "introduction": {
                "word_count": "500-750",
                "components": [
                    "Research context and background",
                    "Problem statement",
                    "Research gap identification",
                    "Purpose/aims of the study",
                    "Significance of the research",
                    "Paper structure overview"
                ],
                "style": "Engaging, logical flow, establishes importance"
            },
            "literature_review": {
                "word_count": "1000-2000",
                "components": [
                    "Theoretical framework",
                    "Previous research synthesis",
                    "Thematic organization",
                    "Critical analysis of existing work",
                    "Identification of patterns, trends, and gaps"
                ],
                "style": "Analytical, not just descriptive; shows relationships between studies"
            },
            "methodology": {
                "word_count": "750-1500",
                "components": [
                    "Research design justification",
                    "Data collection methods",
                    "Analysis techniques",
                    "Limitations and considerations",
                    "Ethical aspects (if applicable)"
                ],
                "style": "Detailed, precise, replicable"
            },
            "results": {
                "word_count": "1000-1500",
                "components": [
                    "Factual presentation of findings",
                    "Statistical analysis (if applicable)",
                    "Tables and figures",
                    "Patterns and trends",
                    "No interpretation (save for discussion)"
                ],
                "style": "Objective, clear, organized logically"
            },
            "discussion": {
                "word_count": "1000-1500",
                "components": [
                    "Interpretation of results",
                    "Relationship to existing literature",
                    "Implications of findings",
                    "Limitations of the study",
                    "Future research directions"
                ],
                "style": "Analytical, connects back to literature, acknowledges constraints"
            },
            "conclusion": {
                "word_count": "300-500",
                "components": [
                    "Summary of key findings",
                    "Contribution to the field",
                    "Broader implications",
                    "Final thought or call to action"
                ],
                "style": "Concise, no new information, emphasizes significance"
            }
        }
        
        return guidelines.get(section_name, {
            "word_count": "Varies",
            "components": ["Context appropriate elements"],
            "style": "Academic, formal"
        })
    
    @staticmethod
    def get_citation_style(style_name: str) -> Dict[str, str]:
        """
        Get citation style guidelines.
        
        Args:
            style_name: Name of citation style
            
        Returns:
            Dictionary with citation style guidelines
        """
        styles = {
            "apa": {
                "in_text": "(Author, Year)",
                "bibliography": "Author, A. (Year). Title. Journal, Volume(Issue), Pages.",
                "latex_style": "\\bibliographystyle{apalike}"
            },
            "mla": {
                "in_text": "(Author Page)",
                "bibliography": "Author. Title. Journal, Volume, Issue, Year, Pages.",
                "latex_style": "\\bibliographystyle{mla}"
            },
            "chicago": {
                "in_text": "(Author Year, Page)",
                "bibliography": "Author. Year. Title. Journal Volume, Issue: Pages.",
                "latex_style": "\\bibliographystyle{chicago}"
            },
            "ieee": {
                "in_text": "[1]",
                "bibliography": "[1] A. Author, \"Title,\" Journal, vol. x, no. x, pp. xxx-xxx, Month Year.",
                "latex_style": "\\bibliographystyle{IEEEtran}"
            }
        }
        
        return styles.get(style_name, styles["apa"])
    
    @staticmethod
    def get_journal_format(journal_name: str) -> Dict[str, Any]:
        """
        Get formatting guidelines for specific journals.
        
        Args:
            journal_name: Name of the journal
            
        Returns:
            Dictionary with journal formatting guidelines
        """
        formats = {
            "nature": {
                "abstract_length": "150-250 words",
                "word_limit": "3000-5000 words",
                "citation_style": "nature",
                "structure": ["abstract", "introduction", "results", "discussion", "methods"],
                "latex_class": "nature"
            },
            "science": {
                "abstract_length": "125 words",
                "word_limit": "4500 words",
                "citation_style": "science",
                "structure": ["abstract", "introduction", "results", "discussion", "materials_and_methods"],
                "latex_class": "science"
            },
            "plos": {
                "abstract_length": "250-300 words",
                "word_limit": "No formal limit",
                "citation_style": "vancouver",
                "structure": ["abstract", "introduction", "methods", "results", "discussion", "conclusion"],
                "latex_class": "plos"
            },
            "ieee": {
                "abstract_length": "150-250 words",
                "word_limit": "8000 words",
                "citation_style": "ieee",
                "structure": ["abstract", "introduction", "related_work", "methodology", "results", "discussion", "conclusion"],
                "latex_class": "IEEEtran"
            }
        }
        
        # Default academic format if journal not found
        return formats.get(journal_name, {
            "abstract_length": "150-250 words",
            "word_limit": "5000-8000 words",
            "citation_style": "apa",
            "structure": ["abstract", "introduction", "literature_review", "methodology", "results", "discussion", "conclusion"],
            "latex_class": "article"
        })