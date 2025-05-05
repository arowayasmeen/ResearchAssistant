import asyncio
import os
from src.research_assistant.draft.generator import ResearchDraftGenerator




async def test_title_generator():
    # Initialize the generator
    generator = ResearchDraftGenerator()
   
    # Define a research topic
    research_topic = "The Impact of Artificial Intelligence on Education"
   
    # Generate title suggestions
    print("Generating outline...")
    outline = await generator.generate_outline(
        research_topic=research_topic,
        paper_type = 'standard'
    )
   
    print("\n==== outline ====\n")
    print({outline})
    print("\n===================================\n")




if __name__ == "__main__":
    asyncio.run(test_title_generator())