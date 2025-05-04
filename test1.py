
import requests
import json

def test_title_generation_api():
    """Test the title generation endpoint"""
    url = "http://localhost:5000/api/draft/generate-titles"
    
    # Define the request payload
    payload = {
        "research_topic": "The Impact of Artificial Intelligence on Education",
        "count": 5
    }
    
    # Make the API request
    print(f"Sending POST request to {url}...")
    try:
        response = requests.post(url, json=payload)
        
        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()
            
            print("\n==== API RESPONSE ====\n")
            print(f"Success: {data['success']}")
            print("\nGenerated Titles:")
            for i, title in enumerate(data['titles'], 1):
                print(f"{i}. {title}")
            print("\n=====================\n")
        else:
            print(f"Request failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
    
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_title_generation_api()