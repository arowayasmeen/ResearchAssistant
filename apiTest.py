"""
Debug script to test the ResearchAssistant API endpoints directly.
"""


import os
import sys
import json
import asyncio
import aiohttp
import logging
from dotenv import load_dotenv


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Add project root to ensure imports work
sys.path.insert(0, os.path.abspath('.'))


# Load environment variables
load_dotenv()


# Check Google API key
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    logger.error("GOOGLE_API_KEY not found in environment variables")
    print("\n\033[91mError: GOOGLE_API_KEY not found!\033[0m")
    print("Please make sure you have a .env file with your GOOGLE_API_KEY set.")
    print("Example: GOOGLE_API_KEY=your_api_key_here\n")
    sys.exit(1)
else:
    logger.info(f"GOOGLE_API_KEY found (length: {len(api_key)})")


# API endpoint configuration
API_BASE_URL = 'http://localhost:5000/api'


async def test_server():
    """Test if the server is running."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_BASE_URL.split('/api')[0]}") as response:
                print(f"\033[92m✓ Server is running at {API_BASE_URL.split('/api')[0]}\033[0m")
                return True
    except Exception as e:
        print(f"\033[91m✗ Server not running or not accessible: {str(e)}\033[0m")
        print("\nPlease start the API server using:")
        print("  python src/research_assistant/api/app.py")
        return False


async def test_generate_titles():
    """Test the generate-titles endpoint."""
    endpoint = f"{API_BASE_URL}/draft/generate-titles"
    data = {
        "research_topic": "The Impact of Artificial Intelligence on Education",
        "count": 3
    }
   
    try:
        timeout = aiohttp.ClientTimeout(total=30)  # 30 second timeout
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(endpoint, json=data) as response:
                result = await response.json()
                if response.status == 200 and result.get('success'):
                    print("\n\033[92m✓ generate-titles endpoint working!\033[0m")
                    print("Suggested titles:")
                    for i, title in enumerate(result.get('titles', []), 1):
                        print(f"  {i}. {title}")
                else:
                    print("\n\033[91m✗ generate-titles endpoint failed!\033[0m")
                    print(f"Status: {response.status}")
                    print(f"Response: {result}")
    except asyncio.TimeoutError:
        print("\n\033[91m✗ generate-titles request timed out after 30 seconds\033[0m")
    except Exception as e:
        print(f"\n\033[91m✗ Error connecting to generate-titles: {str(e)}\033[0m")


async def test_generate_outline():
    """Test the generate-outline endpoint."""
    endpoint = f"{API_BASE_URL}/draft/generate-outline"
    data = {
        "research_topic": "The Impact of Artificial Intelligence on Education",
        "paper_type": "standard"
    }
   
    try:
        timeout = aiohttp.ClientTimeout(total=30)  # 30 second timeout
        async with aiohttp.ClientSession(timeout=timeout) as session:
            print("\nRequesting outline generation...")
            async with session.post(endpoint, json=data) as response:
                print(f"Response status: {response.status}")
                result = await response.json()
               
                if response.status == 200 and result.get('success'):
                    print("\033[92m✓ generate-outline endpoint working!\033[0m")
                    outline = result.get('outline', '')
                    print("Outline preview (first 200 chars):")
                    print(f"  {outline[:200]}...")
                else:
                    print("\n\033[91m✗ generate-outline endpoint failed!\033[0m")
                    print(f"Status: {response.status}")
                    print(f"Response: {json.dumps(result, indent=2)}")
    except asyncio.TimeoutError:
        print("\n\033[91m✗ generate-outline request timed out after 30 seconds\033[0m")
    except Exception as e:
        print(f"\n\033[91m✗ Error with generate-outline endpoint: {str(e)}\033[0m")
        import traceback
        print(traceback.format_exc())




async def test_generate_paper():
    """Test the generate-paper endpoint."""
    endpoint = f"{API_BASE_URL}/draft/generate-paper"
    data = {
        "research_topic": "The Impact of Artificial Intelligence on Education",
        "paper_type": "standard",
        "literature_summary": {
            "AI adoption": "Many schools have started integrating AI tools to personalize student learning.",
            "Student outcomes": "Mixed evidence exists on how AI impacts measurable academic achievement."
        },
        "research_gaps": [
            "Long-term effects of AI on cognitive development",
            "Biases in AI-based grading systems"
        ]
    }


    try:
        timeout = aiohttp.ClientTimeout(total=400)  # Paper generation may take longer
        async with aiohttp.ClientSession(timeout=timeout) as session:
            print("\nRequesting full paper generation...")
            async with session.post(endpoint, json=data) as response:
                print(f"Response status: {response.status}")
                result = await response.json()


                if response.status == 200 and result.get('success'):
                    print("\033[92m✓ generate-paper endpoint working!\033[0m")
                    sections = result.get('sections', {})
                    print("Paper Sections:")
                    for i, (section, content) in enumerate(sections.items(), 1):
                        print(f"  {i}. {section} (first 100 chars): {content[:100]}...")
                else:
                    print("\n\033[91m✗ generate-paper endpoint failed!\033[0m")
                    print(f"Status: {response.status}")
                    print(f"Response: {json.dumps(result, indent=2)}")
    except asyncio.TimeoutError:
        print("\n\033[91m✗ generate-paper request timed out\033[0m")
    except Exception as e:
        print(f"\n\033[91m✗ Error with generate-paper endpoint: {str(e)}\033[0m")
        import traceback
        print(traceback.format_exc())


async def run_tests():
    """Run all API tests."""
    server_running = await test_server()
    if not server_running:
        return
   
    # Run tests with delay between them
    await test_generate_titles()
    # Add a small delay between tests
    await asyncio.sleep(1)
    await test_generate_outline()


    await asyncio.sleep(1)
    await test_generate_paper()


def main():
    """Run all tests sequentially."""
    print("\n\033[1m======= ResearchAssistant API Debug Tool =======\033[0m")
    print("Testing if the API server is running...")
   
    # Use a new event loop for the entire testing process
    loop = asyncio.new_event_loop()

    asyncio.set_event_loop(loop)
   
    try:
        loop.run_until_complete(run_tests())
    except KeyboardInterrupt:
        print("\nTests interrupted by user.")
    except Exception as e:
        print(f"\n\033[91mUnexpected error: {str(e)}\033[0m")
        import traceback
        print(traceback.format_exc())
    finally:
        loop.close()
   
    print("\n\033[1m======= Debug Complete =======\033[0m\n")


if __name__ == "__main__":
    main()