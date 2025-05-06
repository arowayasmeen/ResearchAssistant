import asyncio
import os
from src.research_assistant.draft.generator import ResearchDraftGenerator




async def test_paper():
    # Initialize the generator
    generator = ResearchDraftGenerator()
   
    # Define a research topic
    research_topic = "The Impact of Artificial Intelligence on Education"
   
    # Generate title suggestions
    print("Generating draft...")
    paper = await generator.generate_paper(
        research_topic=research_topic,
        paper_type = 'standard'
    )
   
    print("\n==== paper ====\n")
    print(paper)
    print("\n===================================\n")




if __name__ == "__main__":
    asyncio.run(test_paper())