import asyncio
from src.research_assistant.draft.generator import ResearchDraftGenerator

async def test_api_functionality():
    generator = ResearchDraftGenerator()
    research_topic = "The Impact of Artificial Intelligence on Education"
    paper_type = "standard"

    # Run both functions concurrently
    titles_task = generator.generate_title_suggestions(research_topic=research_topic)
    outline_task = generator.generate_outline(research_topic=research_topic, paper_type=paper_type)

    titles, outline = await asyncio.gather(titles_task, outline_task)

    print("\n==== TITLES ====\n")
    print(titles)
    print("\n==== OUTLINE ====\n")
    print(outline)

if __name__ == "__main__":
    asyncio.run(test_api_functionality())