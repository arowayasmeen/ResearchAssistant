import asyncio
import os
from src.research_assistant.draft.generator import ResearchDraftGenerator

async def test_api_functionality():
    # Initialize the generator
    generator = ResearchDraftGenerator()
   
    # Define a research topic
    research_topic = "The Impact of Artificial Intelligence on Education"
    paper_type = "standard"
   
    # Test generate_outline functionality
    print("Generating outline...")
    outline = await generator.generate_outline(
        research_topic=research_topic,
        paper_type=paper_type
    )
   
    print("\n==== OUTLINE ====\n")
    print(outline)
    print("\n===================================\n")

    # Test generate_title_suggestions functionality
    print("Generating title suggestions...")
    titles = await generator.generate_title_suggestions(
        research_topic=research_topic,
        count=3
    )
   
    print("\n==== TITLES ====\n")
    for i, title in enumerate(titles, 1):
        print(f"{i}. {title}")
    print("\n===================================\n")

if __name__ == "__main__":
    asyncio.run(test_api_functionality())