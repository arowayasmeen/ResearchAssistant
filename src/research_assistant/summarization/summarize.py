from google import genai
from google.genai import types
import pathlib

# Environment imports
import os

from dotenv import load_dotenv

# Loading environment variables
load_dotenv()
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY").strip('=')[1:-1]

client = genai.Client(api_key=GEMINI_API_KEY)


# Retrieve the PDF
file_path = pathlib.Path('/home/arowayasmeen/research/ResearchAssistant/exports/samplepdfs/SMILES-Prompting A Novel Approach to LLM Jailbreak Attacks in Chemical Synthesis.pdf')

# # Upload the PDF using the File API
sample_file = client.files.upload(
  file=file_path,
)

prompt="""Please provide a comprehensive summary of the following research paper. 
        Include:
        1. The main research question or objective
        2. Key methodology used
        3. Major findings and results
        4. Significant conclusions and implications
        
        Keep the summary concise and focused on the most important information."""

response = client.models.generate_content(
  model="gemini-2.0-flash",
  contents=[sample_file, prompt])
print(response.text)