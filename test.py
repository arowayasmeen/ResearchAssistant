import asyncio
import os
from src.research_assistant.draft.generator import ResearchDraftGenerator


async def test_generator():
    # Initialize without fallback to use the actual Google API
    generator = ResearchDraftGenerator()
    
    # Define a simple research topic
    research_topic = "The Impact of Artificial Intelligence on Education"
    
    # Generate an abstract
    print("Generating abstract...")
    abstract = await generator.generate_section(
        research_topic=research_topic,
        section_type="abstract"
    )
    
    print("\n==== GENERATED ABSTRACT ====\n")
    print(abstract)
    print("\n===========================\n")
    
    # Generate an introduction too (keeping it small for free tier usage)
    print("Generating introduction...")
    introduction = await generator.generate_section(
        research_topic=research_topic,
        section_type="introduction"
    )
    
    print("\n==== GENERATED INTRODUCTION ====\n")
    print(introduction)
    print("\n================================\n")

if __name__ == "__main__":
    asyncio.run(test_generator())