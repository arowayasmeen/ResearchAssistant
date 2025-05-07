import uuid
from typing import Dict, List, Any, Optional, Tuple, Set
import re

from models import ProcessedPDF, MethodContribution, ResearchIdea, Reference


class KnowledgeBase:
    """
    Simple in-memory knowledge base to store and retrieve information.
    """
    
    def __init__(self):
        """Initialize the knowledge base with empty storage."""
        self.papers = {}  # id -> paper data
        self.contributions = {}  # id -> contribution data
        self.concepts = {}  # id -> concept data
        self.user_focus = None
    
    def add_pdf_data(self, processed_pdfs: List[ProcessedPDF]) -> None:
        """
        Add data from processed PDFs to the knowledge base.
        
        Args:
            processed_pdfs: List of processed PDF objects
        """
        for pdf in processed_pdfs:
            # Create an entry for the paper
            paper_id = f"paper_{uuid.uuid4()}"
            
            self.papers[paper_id] = {
                "title": pdf.metadata.get("title", "Untitled Document"),
                "authors": pdf.metadata.get("authors", []),
                "date": pdf.metadata.get("date", ""),
                "file_path": pdf.file_path,
                "sections": pdf.sections,
                "full_text": pdf.full_text
            }
            
            # Extract and store concepts
            concepts = self._extract_concepts(pdf.full_text)
            for concept in concepts:
                concept_id = f"concept_{uuid.uuid4()}"
                self.concepts[concept_id] = {
                    "name": concept,
                    "related_papers": [paper_id]
                }
            
            # Store contributions
            for contribution in pdf.methodological_contributions:
                self.contributions[contribution.id] = {
                    "type": contribution.type,
                    "name": contribution.name or f"Unnamed {contribution.type}",
                    "description": contribution.description,
                    "problem_solved": contribution.problem_solved,
                    "source_paper_id": paper_id,
                    "related_concepts": self._find_related_concepts(contribution.description, concepts)
                }
    
    def check_topic_coherence(self) -> Tuple[bool, List[str]]:
        """
        Check if the documents in the knowledge base focus on coherent topics.
        
        Returns:
            Tuple (is_coherent, list_of_topics)
        """
        if not self.papers:
            return True, []
        
        # Simple implementation - extract top concepts
        all_concepts = set()
        for paper_id, paper in self.papers.items():
            concepts = self._extract_concepts(paper.get("full_text", ""))
            all_concepts.update(concepts)
        
        # Get top concepts by frequency
        concept_counts = {}
        for concept_id, concept in self.concepts.items():
            name = concept.get("name", "")
            if name:
                concept_counts[name] = concept_counts.get(name, 0) + 1
        
        # Sort by frequency
        sorted_concepts = sorted(concept_counts.items(), key=lambda x: x[1], reverse=True)
        top_concepts = [concept for concept, count in sorted_concepts[:5]]
        
        # For simplicity, consider coherent if we have few papers or few concepts
        is_coherent = len(self.papers) <= 2 or len(all_concepts) < 10
        
        return is_coherent, top_concepts
    
    def set_user_focus(self, focus: str) -> None:
        """
        Set the user-specified focus area.
        
        Args:
            focus: Focus area string
        """
        self.user_focus = focus
    
    def get_target_problem_goal(self) -> str:
        """
        Get the main problem or goal based on user focus or inferred from documents.
        
        Returns:
            Problem/goal description
        """
        if self.user_focus:
            return f"Advancing research in {self.user_focus}"
        
        # If no user focus, try to infer from papers
        if not self.papers:
            return "General research advancement"
        
        # Take the problem from the first contribution if available
        if self.contributions:
            first_contribution = next(iter(self.contributions.values()))
            if first_contribution.get("problem_solved"):
                return first_contribution.get("problem_solved")
        
        # Otherwise, use the title of the first paper
        first_paper = next(iter(self.papers.values()))
        return f"Advancing research in {first_paper.get('title', 'the field')}"
    
    def get_focused_keywords(self) -> List[str]:
        """
        Get keywords relevant to the user focus.
        
        Returns:
            List of relevant keywords
        """
        if not self.user_focus:
            # Return all concept names
            return [concept.get("name", "") for concept in self.concepts.values()]
        
        # Filter concepts by relevance to user focus
        focus_keywords = self.user_focus.lower().split()
        
        relevant_concepts = []
        for concept in self.concepts.values():
            name = concept.get("name", "").lower()
            if any(keyword in name for keyword in focus_keywords):
                relevant_concepts.append(concept.get("name", ""))
        
        # If no relevant concepts found, return all
        if not relevant_concepts:
            return [concept.get("name", "") for concept in self.concepts.values()]
        
        return relevant_concepts
    
    def get_methodological_contributions(self) -> List[MethodContribution]:
        """
        Get methodological contributions, optionally filtered by user focus.
        
        Returns:
            List of MethodContribution objects
        """
        contributions = []
        
        for contrib_id, contrib_data in self.contributions.items():
            # Filter by user focus if set
            if self.user_focus:
                # Skip if not relevant to focus
                if not self._is_relevant_to_focus(contrib_data, self.user_focus):
                    continue
            
            # Create MethodContribution object
            contribution = MethodContribution(
                id=contrib_id,
                type=contrib_data.get("type", "Method"),
                name=contrib_data.get("name"),
                description=contrib_data.get("description", ""),
                problem_solved=contrib_data.get("problem_solved"),
                source_paper_id=contrib_data.get("source_paper_id", ""),
                location_in_paper=""
            )
            
            contributions.append(contribution)
        
        return contributions
    
    def _extract_concepts(self, text: str) -> List[str]:
        """
        Extract concepts from text (simplified implementation).
        
        Args:
            text: Text to analyze
            
        Returns:
            List of concept strings
        """
        # Simplified concept extraction - look for capitalized phrases and technical terms
        concepts = set()
        
        # Capitalized phrases (potential technical terms)
        for match in re.finditer(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b', text):
            concept = match.group(1)
            # Filter out common words and short phrases
            if len(concept) > 3 and concept not in ["Introduction", "Abstract", "Conclusion"]:
                concepts.add(concept)
        
        # Look for common NLP/ML terms
        common_terms = ["machine learning", "deep learning", "neural network", "algorithm", 
                        "natural language processing", "computer vision", "reinforcement learning"]
        
        for term in common_terms:
            if re.search(r'\b' + re.escape(term) + r'\b', text, re.IGNORECASE):
                concepts.add(term)
        
        return list(concepts)
    
    def _find_related_concepts(self, text: str, all_concepts: List[str]) -> List[str]:
        """
        Find concepts that appear in the given text.
        
        Args:
            text: Text to search
            all_concepts: List of all concepts to check
            
        Returns:
            List of related concept names
        """
        related = []
        for concept in all_concepts:
            if re.search(r'\b' + re.escape(concept) + r'\b', text, re.IGNORECASE):
                related.append(concept)
        return related
    
    def _is_relevant_to_focus(self, contribution_data: Dict[str, Any], focus: str) -> bool:
        """
        Check if a contribution is relevant to the user focus.
        
        Args:
            contribution_data: Contribution data dictionary
            focus: User focus string
            
        Returns:
            True if relevant, False otherwise
        """
        focus_terms = focus.lower().split()
        
        # Check name, description, and problem
        name = contribution_data.get("name", "").lower()
        description = contribution_data.get("description", "").lower()
        problem = contribution_data.get("problem_solved", "").lower()
        
        # Check if any focus term appears in the contribution data
        for term in focus_terms:
            if term in name or term in description or term in problem:
                return True
                
        # Check related concepts
        related_concepts = contribution_data.get("related_concepts", [])
        for concept in related_concepts:
            if any(term in concept.lower() for term in focus_terms):
                return True
        
        return False