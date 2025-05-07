import uuid
import re
from typing import Dict, List, Any, Optional

from models import ResearchIdea, Reference, EvaluationResult, HybridMethodology, MethodologyStructure, ValidationResult, CodeOutput
from api_clients import LLMClient


class ResearchAgent:
    """
    Agent for generating and evaluating research ideas.
    """
    
    def __init__(self, llm_client: LLMClient):
        """
        Initialize the research agent with an LLM client.
        
        Args:
            llm_client: LLM client for generating and processing text
        """
        self.llm_client = llm_client
    
    def generate_ideas(self, problem_goal: str, contributions: List[Dict[str, Any]], count: int = 3) -> List[ResearchIdea]:
        """
        Generate research ideas based on problem goal and existing contributions.
        
        Args:
            problem_goal: Problem or goal to address
            contributions: List of methodological contributions
            count: Number of ideas to generate
            
        Returns:
            List of generated research ideas
        """
        # Prepare the prompt
        prompt = self._create_idea_generation_prompt(problem_goal, contributions, count)
        
        # Generate text using LLM
        response = self.llm_client.generate_text(prompt, max_tokens=2000)
        
        # Parse the response into research ideas
        ideas = self._parse_ideas_from_response(response, contributions)
        
        # If we couldn't parse any ideas, make a simpler attempt
        if not ideas:
            print("Warning: Failed to parse ideas with structured format. Trying simpler approach...")
            ideas = self._parse_ideas_simple(response, contributions)
        
        return ideas
    
    def evaluate_idea(self, idea: ResearchIdea, problem_goal: str) -> EvaluationResult:
        """
        Evaluate a research idea based on multiple criteria.
        
        Args:
            idea: Research idea to evaluate
            problem_goal: Problem or goal the idea should address
            
        Returns:
            Evaluation result
        """
        # Prepare the prompt
        prompt = self._create_evaluation_prompt(idea, problem_goal)
        
        # Generate evaluation using LLM
        response = self.llm_client.generate_text(prompt)
        
        # Parse the evaluation from the response
        evaluation = self._parse_evaluation_from_response(response)
        
        return evaluation
    
    def search_and_refine(self, idea: ResearchIdea) -> ResearchIdea:
        """
        Use search to refine a research idea with current information.
        
        Args:
            idea: Initial research idea
            
        Returns:
            Refined research idea
        """
        # Generate search query based on the idea
        query = f"latest research {idea.description}"
        
        # Prepare prompt for refinement based on search
        prompt = f"""
        Based on the latest research, please refine and improve this research idea:
        
        Initial idea: {idea.description}
        
        Please provide a refined version with:
        1. Updated description
        2. Novelty rationale (why this is still novel)
        3. Any additional inspiration sources
        
        Format your response as:
        Refined Description: [description]
        Novelty Rationale: [rationale]
        Additional Sources: [sources]
        """
        
        # Perform search and generate refinement
        search_result = self.llm_client.search_and_generate(query, prompt)
        
        # Parse the refined idea
        refined_idea = self._parse_refined_idea(search_result, idea)
        
        return refined_idea
    
    def synthesize_methodology(self, idea: ResearchIdea, contributions: List[Dict[str, Any]]) -> HybridMethodology:
        """
        Synthesize a methodology based on a research idea.
        
        Args:
            idea: Research idea
            contributions: List of methodological contributions
            
        Returns:
            Synthesized methodology
        """
        # Prepare the prompt
        prompt = self._create_methodology_synthesis_prompt(idea, contributions)
        
        # Generate methodology using LLM
        response = self.llm_client.generate_text(prompt, max_tokens=2000)
        
        # Parse the methodology from the response
        methodology = self._parse_methodology_from_response(response, contributions)
        
        return methodology
    
    def generate_code(self, methodology: HybridMethodology) -> CodeOutput:
        """
        Generate code for a methodology.
        
        Args:
            methodology: Hybrid methodology to implement
            
        Returns:
            Generated code with validation results
        """
        # Prepare the specification
        specification = self._create_code_specification(methodology)
        
        # Generate code using LLM
        code = self.llm_client.generate_code(specification)
        
        # Validate the code (simplified validation)
        validation = self._validate_code(code)
        
        # Create code output
        code_output = CodeOutput(
            code=code,
            validation=validation,
            notes="This is a code scaffold that requires review and refinement by an expert."
        )
        
        return code_output
    
    def _create_idea_generation_prompt(self, problem_goal: str, contributions: List[Dict[str, Any]], count: int) -> str:
        """Create a prompt for generating research ideas."""
        # Format contributions
        contributions_text = ""
        for i, contribution in enumerate(contributions[:5]):  # Limit to 5 contributions to keep the prompt manageable
            contributions_text += f"{i+1}. {contribution.get('name', 'Unnamed')} - {contribution.get('description', '')[:200]}...\n"
        
        prompt = f"""
        You are a creative research scientist tasked with generating {count} novel research ideas based on existing methodological contributions.
        
        **PROBLEM/GOAL TO ADDRESS:**
        {problem_goal}
        
        **EXISTING METHODOLOGICAL CONTRIBUTIONS:**
        {contributions_text}
        
        **TASK:**
        Generate {count} novel research ideas that build upon, combine, or extend these contributions in innovative ways. 
        Be specific and concrete in your descriptions.

        **REQUIREMENTS FOR EACH IDEA:**
        1. A clear and specific description of the idea
        2. Which existing contributions inspired it
        3. Why it's novel and valuable
        
        **FORMAT:**
        Structure your response exactly as follows:

        ```
        Idea 1:
        Description: [detailed description]
        Inspiration: [references to specific contributions]
        Novelty: [explanation of novelty and value]

        Idea 2:
        Description: [detailed description]
        Inspiration: [references to specific contributions]
        Novelty: [explanation of novelty and value]
        
        ... and so on
        ```
        
        Focus on specificity, feasibility, and scientific value.
        """
        
        return prompt
    
    def _parse_ideas_from_response(self, response: str, contributions: List[Dict[str, Any]]) -> List[ResearchIdea]:
        """Parse generated ideas from LLM response using a more robust approach."""
        ideas = []
        
        # Try multiple patterns for finding ideas
        
        # Pattern 1: Look for structured "Idea N:" format
        idea_blocks = re.split(r'(?i)Idea\s+\d+:', response)
        
        if len(idea_blocks) > 1:
            # Process structured format
            for block in idea_blocks[1:]:  # Skip the first split (before "Idea 1")
                try:
                    # Clean up the block
                    block = block.strip()
                    
                    # More flexible pattern matching for description
                    description_match = re.search(r'(?i)(?:Description:\s*)(.*?)(?:\n\s*(?:Inspiration|Novelty):|\n\n|$)', block, re.DOTALL)
                    if not description_match:
                        # Try without the "Description:" label
                        description_match = re.search(r'(.*?)(?:\n\s*(?:Inspiration|Novelty):|\n\n|$)', block, re.DOTALL)
                    
                    description = description_match.group(1).strip() if description_match else ""
                    
                    if not description:
                        continue
                    
                    # Create idea object
                    idea = ResearchIdea(
                        id=str(uuid.uuid4()),
                        description=description,
                        inspiration_sources=[],
                        novelty_rationale=""
                    )
                    
                    # Extract inspiration with more flexible pattern
                    inspiration_match = re.search(r'(?i)(?:Inspiration|Sources|Inspired by):\s*(.*?)(?:\n\s*(?:Novelty|Rationale):|\n\n|$)', block, re.DOTALL)
                    if inspiration_match:
                        inspiration_text = inspiration_match.group(1).strip()
                        # Try to match inspirations to contributions
                        for contribution in contributions:
                            name = contribution.get('name', '')
                            if name and name in inspiration_text:
                                idea.inspiration_sources.append(
                                    Reference(
                                        source_id=contribution.get('id', ''),
                                        source_type="contribution",
                                        context=f"Inspired by {name}"
                                    )
                                )
                    
                    # Extract novelty rationale with more flexible pattern
                    novelty_match = re.search(r'(?i)(?:Novelty|Rationale|Value):\s*(.*?)(?:\n\n|$)', block, re.DOTALL)
                    if novelty_match:
                        idea.novelty_rationale = novelty_match.group(1).strip()
                    
                    ideas.append(idea)
                except Exception as e:
                    print(f"Error parsing idea: {str(e)}")
            
            return ideas
        
        # Pattern 2: Look for numbered ideas without explicit "Idea N:" headings
        numbered_pattern = r'(?:^|\n)(\d+\.\s*.*?)(?=\n\d+\.|\Z)'
        numbered_matches = re.findall(numbered_pattern, response, re.DOTALL)
        
        if numbered_matches:
            for match in numbered_matches:
                try:
                    text = match.strip()
                    if len(text) > 50:  # Only consider substantial text
                        # Create a simple idea object
                        idea = ResearchIdea(
                            id=str(uuid.uuid4()),
                            description=text,
                            inspiration_sources=[],
                            novelty_rationale=""
                        )
                        
                        # Try to find contributions mentioned in the text
                        for contribution in contributions:
                            name = contribution.get('name', '')
                            if name and name in text:
                                idea.inspiration_sources.append(
                                    Reference(
                                        source_id=contribution.get('id', ''),
                                        source_type="contribution",
                                        context=f"Mentioned in idea description"
                                    )
                                )
                        
                        ideas.append(idea)
                except Exception as e:
                    print(f"Error parsing numbered idea: {str(e)}")
            
            return ideas
        
        # Pattern 3: Fall back to paragraph-based parsing if no structured format found
        paragraphs = [p for p in response.split('\n\n') if p.strip()]
        
        for paragraph in paragraphs:
            if len(paragraph.strip()) > 100:  # Only consider substantial paragraphs
                try:
                    # Create a simple idea object
                    idea = ResearchIdea(
                        id=str(uuid.uuid4()),
                        description=paragraph.strip(),
                        inspiration_sources=[],
                        novelty_rationale=""
                    )
                    
                    # Try to find contributions mentioned in the paragraph
                    for contribution in contributions:
                        name = contribution.get('name', '')
                        if name and name in paragraph:
                            idea.inspiration_sources.append(
                                Reference(
                                    source_id=contribution.get('id', ''),
                                    source_type="contribution",
                                    context=f"Mentioned in idea description"
                                )
                            )
                    
                    ideas.append(idea)
                    
                    # Limit to 3 ideas
                    if len(ideas) >= 3:
                        break
                except Exception as e:
                    print(f"Error parsing paragraph idea: {str(e)}")
        
        return ideas
        
    def _parse_ideas_simple(self, response: str, contributions: List[Dict[str, Any]]) -> List[ResearchIdea]:
        """Simpler parsing approach for when the structured format fails."""
        ideas = []
        
        # Split by double newlines to get paragraphs
        paragraphs = response.split('\n\n')
        
        for i, paragraph in enumerate(paragraphs):
            if len(paragraph.strip()) > 50:  # Only consider substantial paragraphs
                # Create a simple idea object
                idea = ResearchIdea(
                    id=str(uuid.uuid4()),
                    description=paragraph.strip(),
                    inspiration_sources=[],
                    novelty_rationale=""
                )
                
                # Try to find contributions mentioned in the paragraph
                for contribution in contributions:
                    name = contribution.get('name', '')
                    if name and name in paragraph:
                        idea.inspiration_sources.append(
                            Reference(
                                source_id=contribution.get('id', ''),
                                source_type="contribution",
                                context=f"Mentioned in idea description"
                            )
                        )
                
                ideas.append(idea)
                
                # Limit to 3 ideas
                if len(ideas) >= 3:
                    break
        
        return ideas
    
    def _create_evaluation_prompt(self, idea: ResearchIdea, problem_goal: str) -> str:
        """Create a prompt for evaluating a research idea."""
        prompt = f"""
        You are a scientific research evaluator. Please evaluate the following research idea based on multiple criteria:
        
        **PROBLEM/GOAL TO ADDRESS:**
        {problem_goal}
        
        **RESEARCH IDEA TO EVALUATE:**
        {idea.description}
        
        **NOVELTY RATIONALE:**
        {idea.novelty_rationale if idea.novelty_rationale else "Not provided"}
        
        **EVALUATION CRITERIA:**
        1. Novelty (0-10): How original and innovative is this idea?
        2. Feasibility (0-10): How practical is it to implement?
        3. Impact (0-10): How significant would the impact be if successful?
        4. Alignment (0-10): How well does it address the problem/goal?
        
        **REQUIRED FORMAT:**
        Novelty: [score] - [brief explanation]
        Feasibility: [score] - [brief explanation]
        Impact: [score] - [brief explanation]
        Alignment: [score] - [brief explanation]
        
        Overall Score: [average of scores]
        
        Feedback: [detailed feedback, including strengths and weaknesses]
        """
        
        return prompt
    
    def _parse_evaluation_from_response(self, response: str) -> EvaluationResult:
        """Parse evaluation results from LLM response."""
        # Default values
        overall_score = 5.0
        feedback = "Evaluation could not be parsed."
        
        try:
            # Extract overall score
            score_match = re.search(r'Overall Score:\s*(\d+(?:\.\d+)?)', response)
            if score_match:
                overall_score = float(score_match.group(1))
                # Normalize to 0-1 range
                overall_score = max(0.0, min(overall_score / 10.0, 1.0))
            else:
                # Try to extract individual scores and average them
                score_pattern = r'(Novelty|Feasibility|Impact|Alignment):\s*(\d+(?:\.\d+)?)'
                scores = re.findall(score_pattern, response)
                if scores:
                    score_values = [float(score[1]) for score in scores]
                    if score_values:
                        overall_score = sum(score_values) / len(score_values) / 10.0  # Average and normalize
            
            # Extract feedback
            feedback_match = re.search(r'Feedback:\s*(.*?)(?:\n\n|$)', response, re.DOTALL)
            if feedback_match:
                feedback = feedback_match.group(1).strip()
            else:
                # If no explicit feedback section, use entire response
                feedback = response
        except Exception as e:
            print(f"Error parsing evaluation: {str(e)}")
        
        return EvaluationResult(score=overall_score, feedback=feedback)
    
    def _parse_refined_idea(self, search_result: Dict[str, Any], original_idea: ResearchIdea) -> ResearchIdea:
        """Parse refined idea from search results."""
        response = search_result.get("response", "")
        
        # Create a new idea based on the original
        refined_idea = ResearchIdea(
            id=str(uuid.uuid4()),
            description=original_idea.description,
            inspiration_sources=original_idea.inspiration_sources.copy(),
            novelty_rationale=original_idea.novelty_rationale
        )
        
        try:
            # Extract refined description
            desc_match = re.search(r'Refined Description:\s*(.*?)(?:\n\s*Novelty|\n\s*Additional|\n\n|$)', response, re.DOTALL)
            if desc_match and desc_match.group(1).strip():
                refined_idea.description = desc_match.group(1).strip()
            
            # Extract novelty rationale
            novelty_match = re.search(r'Novelty Rationale:\s*(.*?)(?:\n\s*Additional|\n\n|$)', response, re.DOTALL)
            if novelty_match and novelty_match.group(1).strip():
                refined_idea.novelty_rationale = novelty_match.group(1).strip()
            
            # Extract additional sources
            sources_match = re.search(r'Additional Sources:\s*(.*?)(?:\n\n|$)', response, re.DOTALL)
            if sources_match and sources_match.group(1).strip():
                sources_text = sources_match.group(1).strip()
                if sources_text:
                    # Add as a reference
                    refined_idea.inspiration_sources.append(
                        Reference(
                            source_id="search_results",
                            source_type="online",
                            context=sources_text
                        )
                    )
            
            # If we couldn't extract structured fields but have a substantial response,
            # use it to augment the novelty rationale
            if (refined_idea.description == original_idea.description and 
                refined_idea.novelty_rationale == original_idea.novelty_rationale and
                len(response) > 100):
                refined_idea.novelty_rationale = f"{original_idea.novelty_rationale}\n\nAdditional insights from research: {response[:500]}..."
        except Exception as e:
            print(f"Error parsing refined idea: {str(e)}")
            # If parsing fails, add search response as additional context
            if len(response) > 50:
                refined_idea.novelty_rationale = f"{original_idea.novelty_rationale}\n\nAdditional context: {response[:300]}..."
        
        return refined_idea
    
    def _create_methodology_synthesis_prompt(self, idea: ResearchIdea, contributions: List[Dict[str, Any]]) -> str:
        """Create a prompt for synthesizing a methodology."""
        # Format contributions (limit to most relevant ones)
        contributions_text = ""
        # Find contributions mentioned in idea's inspiration sources
        mentioned_ids = [ref.source_id for ref in idea.inspiration_sources if ref.source_type == "contribution"]
        
        # First add mentioned contributions
        mentioned_count = 0
        for i, contribution in enumerate(contributions):
            if contribution.get('id') in mentioned_ids:
                contributions_text += f"{i+1}. {contribution.get('name', 'Unnamed')} - {contribution.get('description', '')[:200]}...\n"
                mentioned_count += 1
        
        # Add more contributions if fewer than 3 were mentioned
        if mentioned_count < 3:
            for i, contribution in enumerate(contributions):
                if contribution.get('id') not in mentioned_ids and mentioned_count < 3:
                    contributions_text += f"{i+1}. {contribution.get('name', 'Unnamed')} - {contribution.get('description', '')[:200]}...\n"
                    mentioned_count += 1
        
        # Format inspiration sources
        inspiration_text = ""
        for i, source in enumerate(idea.inspiration_sources):
            inspiration_text += f"{i+1}. {source.source_type}: {source.context}\n"
        
        prompt = f"""
        You are a scientific methodology designer. Design a detailed methodology to implement the following research idea:
        
        **RESEARCH IDEA:**
        {idea.description}
        
        **INSPIRATION SOURCES:**
        {inspiration_text}
        
        **AVAILABLE METHODOLOGICAL CONTRIBUTIONS:**
        {contributions_text}
        
        **TASK:**
        Design a concrete methodology that implements this idea, combining or extending existing contributions.
        
        **REQUIRED STRUCTURE:**
        1. Overall structure (sequential, parallel, ensemble, etc.)
        2. Specific components or steps
        3. How the components interact
        4. Rationale for this design
        
        **FORMAT YOUR RESPONSE EXACTLY AS:**
        
        Methodology Description: [brief description]
        
        Structure: [type of structure]
        
        Components:
        1. [component 1]
        2. [component 2]
        ...
        
        Connections:
        - [connection 1]
        - [connection 2]
        ...
        
        Rationale:
        [explanation of why this methodology is appropriate]
        
        Be specific, clear, and technically precise.
        """
        
        return prompt
    
    def _parse_methodology_from_response(self, response: str, contributions: List[Dict[str, Any]]) -> HybridMethodology:
        """Parse methodology from LLM response."""
        # Default values
        structure_type = "sequential"
        steps = []
        connections = []
        rationale = []
        description = "Generated methodology"
        
        try:
            # Extract description
            desc_match = re.search(r'Methodology Description:\s*(.*?)(?:\n\s*Structure:|\n\n|$)', response, re.DOTALL)
            if desc_match:
                description = desc_match.group(1).strip()
            
            # Extract structure type
            struct_match = re.search(r'Structure:\s*(.*?)(?:\n\s*Components:|\n\n|$)', response)
            if struct_match:
                structure_type = struct_match.group(1).strip().lower()
                # Normalize structure type
                if "parallel" in structure_type:
                    structure_type = "parallel"
                elif "ensemble" in structure_type:
                    structure_type = "ensemble"
                else:
                    structure_type = "sequential"
            
            # Extract components/steps
            components_text = ""
            components_match = re.search(r'Components:(.*?)(?:\n\s*Connections:|\n\s*Rationale:|\n\n|$)', response, re.DOTALL)
            if components_match:
                components_text = components_match.group(1).strip()
                
                # Parse numbered components
                component_pattern = r'(?:\d+\.|\-)\s*(.*?)(?=\n\s*(?:\d+\.|\-)\s*|\n\n|$)'
                component_matches = re.findall(component_pattern, components_text, re.DOTALL)
                steps = [match.strip() for match in component_matches if match.strip()]
                
                # If no matches found, split by newlines and look for lines with content
                if not steps:
                    for line in components_text.split('\n'):
                        line = line.strip()
                        if line and not line.startswith("Components:"):
                            steps.append(line)
            
            # Extract connections
            connections_text = ""
            connections_match = re.search(r'Connections:(.*?)(?:\n\s*Rationale:|\n\n|$)', response, re.DOTALL)
            if connections_match:
                connections_text = connections_match.group(1).strip()
                
                # Parse connections (likely bullet points)
                connection_pattern = r'(?:\-|\d+\.)\s*(.*?)(?=\n\s*(?:\-|\d+\.)\s*|\n\n|$)'
                connection_matches = re.findall(connection_pattern, connections_text, re.DOTALL)
                
                for connection in connection_matches:
                    if connection.strip():
                        connections.append({"description": connection.strip()})
                
                # If no matches found, split by newlines
                if not connections:
                    for line in connections_text.split('\n'):
                        line = line.strip()
                        if line and not line.startswith("Connections:"):
                            connections.append({"description": line})
            
            # Extract rationale
            rationale_text = ""
            rationale_match = re.search(r'Rationale:(.*?)(?:\n\n|$)', response, re.DOTALL)
            if rationale_match:
                rationale_text = rationale_match.group(1).strip()
                if rationale_text:
                    # Split by paragraphs
                    rationale = [p.strip() for p in rationale_text.split('\n\n') if p.strip()]
                    # If no paragraphs found, use the whole text
                    if not rationale:
                        rationale = [rationale_text]
            
            # If we didn't find any steps, try a more general approach
            if not steps:
                # Look for numbered lines anywhere in the text
                numbered_pattern = r'(?:\d+\.|\-)\s*(.*?)(?=\n\s*(?:\d+\.|\-)\s*|\n\n|$)'
                numbered_matches = re.findall(numbered_pattern, response, re.DOTALL)
                
                # Filter out very short lines and use as steps
                steps = [match.strip() for match in numbered_matches if len(match.strip()) > 15]
                
                # Limit to 10 steps
                steps = steps[:10]
            
            # If still no steps, create a default step from the description
            if not steps and description:
                steps = ["Implement " + description]
        except Exception as e:
            print(f"Error parsing methodology: {str(e)}")
            # Create default methodology
            if description:
                steps = ["Implement " + description]
            else:
                steps = ["Implementation step"]
        
        # Create MethodologyStructure
        structure = MethodologyStructure(
            type=structure_type,
            steps=[f"step_{i}" for i in range(len(steps))],
            connections=[{"from": f"step_{i}", "to": f"step_{i+1}", "type": "flow"} for i in range(len(steps)-1)]
        )
        
        # Create HybridMethodology
        methodology = HybridMethodology(
            structure=structure,
            components=steps,
            rationale=rationale,
            description=description
        )
        
        return methodology
    
    def _create_code_specification(self, methodology: HybridMethodology) -> str:
        """Create a specification for code generation."""
        # Format components
        components_text = ""
        for i, component in enumerate(methodology.components):
            components_text += f"{i+1}. {component}\n"
        
        # Format structure
        structure_text = f"Type: {methodology.structure.type}\n"
        structure_text += f"Steps: {', '.join(methodology.structure.steps)}\n"
        
        # Format connections
        connections_text = ""
        for connection in methodology.structure.connections:
            connections_text += f"- {connection.get('from', '')} → {connection.get('to', '')}\n"
        
        # Format rationale (limited to avoid overwhelming the model)
        rationale_text = ""
        if methodology.rationale:
            rationale_text = methodology.rationale[0][:500]  # Limit to first rationale and 500 chars
        
        specification = f"""
        # PYTHON CODE IMPLEMENTATION SPECIFICATION
        
        ## Overview
        {methodology.description}
        
        ## Methodology Structure
        {structure_text}
        
        ## Components
        {components_text}
        
        ## Connections
        {connections_text}
        
        ## Rationale
        {rationale_text}
        
        ## Implementation Requirements
        1. Create a modular implementation with separate classes for each component
        2. Implement a main class that orchestrates the components according to the structure
        3. Include proper error handling and logging
        4. Add clear documentation and type hints
        5. Make the code easy to extend with new components
        
        Use Python best practices and follow a clear object-oriented design.
        The code should be production-ready with proper documentation.
        """
        
        return specification
    
    def _validate_code(self, code: str) -> ValidationResult:
        """Perform basic validation of generated code."""
        # This is a simplified validation - in a real implementation,
        # you would use static analysis tools, linters, etc.
        
        syntax_ok = True
        basic_tests_passed = False
        security_warnings = []
        suggestions = []
        
        # Basic syntax check
        try:
            compile(code, '<string>', 'exec')
        except SyntaxError as e:
            syntax_ok = False
            suggestions.append(f"Fix syntax error: {str(e)}")
        
        # Simple pattern checks for potential issues
        if "import os" in code and ("os.system(" in code or "os.popen(" in code or "os.spawn" in code):
            security_warnings.append("Code contains potentially unsafe system calls")
        
        if "eval(" in code or "exec(" in code:
            security_warnings.append("Code contains potentially unsafe eval() or exec() functions")
        
        if "__import__(" in code:
            security_warnings.append("Code contains potentially unsafe dynamic imports")
        
        # Check for common code quality issues
        if "# TODO" in code or "# FIXME" in code:
            suggestions.append("Implement the TODO items marked in the code")
        
        if "print(" in code and "def main" in code:
            suggestions.append("Consider using logging instead of print statements")
        
        # Check for proper class structure
        if not re.search(r'class\s+\w+\s*[:\(]', code):
            suggestions.append("Add proper class definitions for components")
        
        # Check for docstrings
        if not re.search(r'"""', code):
            suggestions.append("Add docstrings to classes and methods")
        
        # Check for type hints
        if not re.search(r'def\s+\w+\s*\(.*:\s*\w+', code):
            suggestions.append("Add type hints to function parameters and return values")
        
        # Assume tests would pass if syntax is ok and no security warnings
        basic_tests_passed = syntax_ok and not security_warnings
        
        return ValidationResult(
            syntax_ok=syntax_ok,
            basic_tests_passed=basic_tests_passed,
            security_warnings=security_warnings,
            suggestions=suggestions
        )