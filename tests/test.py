import asyncio
import os
import json
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
        paper_type='standard'
    )

    # Print the paper
    print("\n==== paper ====\n")
    print(paper)
    print("\n===================================\n")

    # Save the paper to a JSON file
    output_path = "generated_paper.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({"title": research_topic, "content": paper}, f, indent=4, ensure_ascii=False)

    print(f"Paper saved as JSON at: {output_path}")

if __name__ == "__main__":
    asyncio.run(test_paper())