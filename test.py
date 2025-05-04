import asyncio
import os
from src.research_assistant.draft.generator import ResearchDraftGenerator




async def test_title_generator():
    # Initialize the generator
    generator = ResearchDraftGenerator()
   
    # Define a research topic
    research_topic = "The Impact of Artificial Intelligence on Education"
   
    # Generate title suggestions
    print("Generating title suggestions...")
    titles = await generator.generate_title_suggestions(
        research_topic=research_topic,
        count=7  # Let's get 7 suggestions
    )
   
    print("\n==== GENERATED TITLE SUGGESTIONS ====\n")
    for i, title in enumerate(titles, 1):
        print(f"{i}. {title}")
    print("\n===================================\n")




if __name__ == "__main__":
    asyncio.run(test_title_generator())