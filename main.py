import os
import argparse
import json
from typing import List, Dict, Any, Optional

from models import ProcessedPDF, ResearchIdea, ResearchOutput
from api_clients import GeminiClient, OpenAIClient
from document_processor import PDFProcessor
from knowledge_base import KnowledgeBase
from agents import ResearchAgent
os.environ["GEMINI_API_KEY"] = ""

class HybridResearchPlatform:
    """
    Main class for the Hybrid Research Idea Generation Platform.
    """
    
    def __init__(self, gemini_api_key: Optional[str] = None, openai_api_key: Optional[str] = None, gemini_model: Optional[str] = None):
        """
        Initialize the platform with optional API keys.
        
        Args:
            gemini_api_key: API key for Gemini (defaults to env var)
            openai_api_key: API key for OpenAI (defaults to env var)
            gemini_model: Model name for Gemini
        """
        # Initialize components
        self.pdf_processor = PDFProcessor()
        self.knowledge_base = KnowledgeBase()
        
        # Try to initialize Gemini client first, fall back to OpenAI if needed
        try:
            self.llm_client = GeminiClient(api_key=gemini_api_key, model=gemini_model or "gemini-2.5-flash-preview-04-17")
            print("Using Gemini for LLM functions")
        except Exception as e:
            print(f"Failed to initialize Gemini client: {str(e)}")
            try:
                self.llm_client = OpenAIClient(api_key=openai_api_key)
                print("Using OpenAI for LLM functions")
            except Exception as e:
                print(f"Failed to initialize OpenAI client: {str(e)}")
                raise ValueError("Could not initialize any LLM client. Please check API keys.")
        
        # Initialize research agent
        self.research_agent = ResearchAgent(self.llm_client)
    
    def generate_research_output(self, pdf_files: List[str], user_focus: Optional[str] = None) -> ResearchOutput:
        """
        Generate a research output based on provided PDFs.
        
        Args:
            pdf_files: List of PDF file paths
            user_focus: Optional focus area
            
        Returns:
            Research output (idea, methodology, code)
        """
        print(f"Processing {len(pdf_files)} PDF files...")
        
        # Step 1: Process PDFs
        processed_pdfs = self.pdf_processor.process_pdfs(pdf_files)
        if not processed_pdfs:
            raise ValueError("No PDFs could be processed. Please check file paths.")
        
        print(f"Successfully processed {len(processed_pdfs)} PDFs")
        
        # Step 2: Add to knowledge base
        self.knowledge_base.add_pdf_data(processed_pdfs)
        
        # Step 3: Check topic coherence
        is_coherent, topics = self.knowledge_base.check_topic_coherence()
        
        # If user provided focus, set it
        if user_focus:
            self.knowledge_base.set_user_focus(user_focus)
            print(f"User focus set to: {user_focus}")
        elif not is_coherent and topics:
            # If not coherent and no user focus, use first topic as default
            default_focus = topics[0]
            self.knowledge_base.set_user_focus(default_focus)
            print(f"Topics not coherent. Using default focus: {default_focus}")
            print(f"Available topics: {', '.join(topics)}")
        
        # Step 4: Get problem goal
        problem_goal = self.knowledge_base.get_target_problem_goal()
        print(f"Target problem/goal: {problem_goal}")
        
        # Step 5: Get methodological contributions
        contributions = self.knowledge_base.get_methodological_contributions()
        print(f"Found {len(contributions)} methodological contributions")
        
        # Convert contributions to dictionary form for the agent
        contribution_dicts = []
        for contrib in contributions:
            contribution_dicts.append({
                "id": contrib.id,
                "name": contrib.name,
                "type": contrib.type,
                "description": contrib.description
            })
        
        # Step 6: Generate ideas
        print("Generating research ideas...")
        ideas = self.research_agent.generate_ideas(problem_goal, contribution_dicts)
        
        if not ideas:
            raise ValueError("Failed to generate any research ideas")
        
        print(f"Generated {len(ideas)} research ideas")
        
        # Step 7: Evaluate ideas
        print("Evaluating ideas...")
        best_idea = None
        best_score = -1
        
        for idea in ideas:
            print(f"Evaluating idea: {idea.description[:50]}...")
            evaluation = self.research_agent.evaluate_idea(idea, problem_goal)
            print(f"  Score: {evaluation.score:.2f}")
            
            if evaluation.score > best_score:
                best_score = evaluation.score
                best_idea = idea
        
        if not best_idea:
            best_idea = ideas[0]  # Fallback to first idea
        
        print(f"Selected best idea: {best_idea.description[:100]}...")
        
        # Step 8: Refine with search
        print("Refining idea with latest research...")
        refined_idea = self.research_agent.search_and_refine(best_idea)
        print(f"Refined idea: {refined_idea.description[:100]}...")
        
        # Step 9: Synthesize methodology
        print("Synthesizing methodology...")
        methodology = self.research_agent.synthesize_methodology(refined_idea, contribution_dicts)
        print(f"Methodology: {methodology.description}")
        
        # Step 10: Generate code
        print("Generating code...")
        code_output = self.research_agent.generate_code(methodology)
        print(f"Code generated ({len(code_output.code)} characters)")
        
        # Step 11: Create final output
        research_output = ResearchOutput(
            selected_idea=refined_idea,
            synthesized_methodology=methodology,
            generated_code=code_output
        )
        
        return research_output


def main():
    """Main function to run the platform from command line."""
    parser = argparse.ArgumentParser(description='Hybrid Research Idea Generation Platform')
    parser.add_argument('--pdfs', nargs='+', required=True, help='Paths to PDF files')
    parser.add_argument('--focus', help='Optional research focus area')
    parser.add_argument('--output', help='Path to save the output JSON')
    parser.add_argument('--gemini_key', help='Gemini API key (optional)')
    parser.add_argument('--openai_key', help='OpenAI API key (optional)')
    parser.add_argument('--gemini_model', help='Gemini model name (optional)')
    
    args = parser.parse_args()
    
    try:
        # Initialize platform
        platform = HybridResearchPlatform(
            gemini_api_key=args.gemini_key,
            openai_api_key=args.openai_key,
            gemini_model=args.gemini_model
        )
        
        # Generate research output
        output = platform.generate_research_output(args.pdfs, args.focus)
        
        # Print summary
        print("\n=== Research Output Summary ===")
        print(f"Selected Idea: {output.selected_idea.description[:100]}...")
        print(f"Methodology: {output.synthesized_methodology.description}")
        print(f"Code: {len(output.generated_code.code)} characters")
        print(f"Code validity: {'Valid' if output.generated_code.validation.syntax_ok else 'Invalid'}")
        
        # Save output to file if requested
        if args.output:
            # Convert to dictionary for serialization
            output_dict = {
                "idea": {
                    "description": output.selected_idea.description,
                    "novelty_rationale": output.selected_idea.novelty_rationale
                },
                "methodology": {
                    "description": output.synthesized_methodology.description,
                    "type": output.synthesized_methodology.structure.type,
                    "components": output.synthesized_methodology.components,
                    "rationale": output.synthesized_methodology.rationale
                },
                "code": {
                    "text": output.generated_code.code,
                    "valid": output.generated_code.validation.syntax_ok,
                    "notes": output.generated_code.notes
                }
            }
            
            with open(args.output, 'w') as f:
                json.dump(output_dict, f, indent=2)
            
            print(f"Output saved to {args.output}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())