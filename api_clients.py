import os
import json
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union
import re

# Try to import necessary libraries, provide guidance if missing
try:
    from google import genai
    from google.genai import types as google_types
except ImportError:
    print("Error: google-generativeai package not found.")
    print("Please install it using: pip install google-generativeai")
    # Optionally raise the error or exit if the dependency is critical
    raise

try:
    from openai import OpenAI
except ImportError:
    print("Warning: openai package not found.")
    print("OpenAI functionality will be unavailable.")
    print("Install it using: pip install openai")
    OpenAI = None # Set to None if not available


class LLMClient(ABC):
    """Abstract base class for LLM API clients."""

    def __init__(self, api_key: str, model: str):
        """
        Initialize the base client.

        Args:
            api_key: The API key for the LLM service.
            model: The model name to use.
        """
        self.api_key = api_key
        self.model = model

    @abstractmethod
    def generate_text(self, prompt: str, temperature: float = 0.7, max_tokens: int = 1000) -> str:
        """Generate text based on a prompt."""
        pass

    @abstractmethod
    def generate_code(self, specification: str, language: str = "python") -> str:
        """Generate code based on a specification."""
        pass

    @abstractmethod
    def search_and_generate(self, query: str, prompt: str) -> Dict[str, Any]:
        """Perform search and generate text based on search results."""
        pass


class GeminiClient(LLMClient):
    """Client for Google's Gemini API with search and code execution capabilities."""

    def __init__(self, api_key: str = None, model: str = "gemini-1.5-flash-latest"): # Using latest flash model
        """
        Initialize the Gemini client.

        Args:
            api_key: API key for Gemini. Reads from GEMINI_API_KEY env var if None.
            model: The Gemini model to use (e.g., "gemini-1.5-flash-latest", "gemini-1.5-pro-latest").
        """
        # Ensure the google-genai library was imported successfully
        if not genai:
             raise ImportError("Google Generative AI package could not be imported.")

        self.genai = genai
        self.types = google_types

        # Retrieve API key from parameter or environment variable
        api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("API key must be provided or set as GEMINI_API_KEY environment variable")

        super().__init__(api_key=api_key, model=model)

        # Initialize the Gemini client using the retrieved API key
        # No genai.configure() needed; Client() handles configuration.
        try:
            self.client = self.genai.Client(api_key=api_key)
            print(f"GeminiClient initialized with model: {self.model}")
        except Exception as e:
            print(f"Error initializing Gemini Client: {str(e)}")
            raise ValueError(f"Failed to initialize Gemini Client: {str(e)}")


    def generate_text(self, prompt: str, temperature: float = 0.7, max_tokens: int = 2048) -> str: # Increased default max_tokens
        """
        Generate text using the Gemini API via streaming.

        Args:
            prompt: The input prompt for text generation.
            temperature: Controls randomness (0.0 to 1.0). Lower is more deterministic.
            max_tokens: Maximum number of tokens to generate.

        Returns:
            The generated text as a single string, or an error message.
        """
        try:
            # Prepare the content structure for the API call
            contents = [
                self.types.Content(
                    role="user",
                    parts=[self.types.Part.from_text(text=prompt)],
                ),
            ]

            # Configure generation parameters
            generate_content_config = self.types.GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
                # response_mime_type="text/plain", # Usually inferred, can be set if needed
            )

            # Use streaming generation to handle potentially long responses
            stream = self.client.models.generate_content_stream(
                model=self.model,
                contents=contents,
                config=generate_content_config,
            )

            # Accumulate response from stream chunks
            response_text = ""
            for chunk in stream:
                # Ensure chunk.text is not None before appending
                if chunk.text is not None:
                    response_text += chunk.text

            return response_text

        except Exception as e:
            print(f"Error during Gemini text generation: {str(e)}")
            # Consider more specific error handling based on potential API errors
            return f"Error generating text: {str(e)}"

    def generate_code(self, specification: str, language: str = "python") -> str:
        """
        Generate code using the Gemini API via streaming.

        Args:
            specification: Detailed description of the code to generate.
            language: The programming language for the code (e.g., "python").

        Returns:
            The generated code as a single string, or an error message.
        """
        # Construct a prompt specifically for code generation
        prompt = f"Generate {language} code based on the following specification. IMPORTANT: Return only the raw code, without any introductory text, explanations, or markdown formatting (like ```python ... ```).\n\nSpecification:\n{specification}"

        try:
            # Prepare the content structure
            contents = [
                self.types.Content(
                    role="user",
                    parts=[self.types.Part.from_text(text=prompt)],
                ),
            ]

            # Configure generation parameters for code (lower temperature)
            generate_content_config = self.types.GenerateContentConfig(
                temperature=0.2, # Lower temperature for more deterministic code
                # max_output_tokens can be set if needed, defaults might be sufficient
            )

            # Use streaming generation
            stream = self.client.models.generate_content_stream(
                model=self.model,
                contents=contents,
                config=generate_content_config,
            )

            # Accumulate response from stream chunks
            response_code = ""
            for chunk in stream:
                if chunk.text is not None:
                    response_code += chunk.text

            # Basic cleanup: Sometimes models still add markdown fences
            response_code = re.sub(r'^```[a-zA-Z]*\n', '', response_code) # Remove starting ```lang
            response_code = re.sub(r'\n```$', '', response_code) # Remove ending ```
            return response_code.strip() # Remove leading/trailing whitespace

        except Exception as e:
            print(f"Error during Gemini code generation: {str(e)}")
            return f"Error generating code: {str(e)}"

    
    def search_and_generate(self, query: str, prompt: str) -> Dict[str, Any]:
        """
        Perform search using Gemini's Google Search tool and generate text based on results.
        
        Args:
            query: The search query.
            prompt: The prompt guiding the generation based on search results.
        
        Returns:
            A dictionary containing the generated response and placeholder for search results.
        """
        try:
            # Combine query and prompt for clarity to the model
            combined_prompt = f"Based on a Google Search for '{query}', please answer the following question or complete the task: {prompt}"
            
            # Prepare the content structure
            contents = [
                self.types.Content(
                    role="user",
                    parts=[self.types.Part.from_text(text=combined_prompt)],
                ),
            ]
            
            # Define the Google Search tool
            tools = [
                self.types.Tool(
                    google_search=self.types.GoogleSearch()  # Basic search tool configuration
                )
            ]
            
            # Configure generation parameters
            generate_content_config = self.types.GenerateContentConfig(
                temperature=0.7,  # Standard temperature for creative/informative text
                tools=tools,      # Move tools to config rather than as a separate parameter
            )
            
            # Use streaming generation
            print(f"Performing search for: {query}")
            stream = self.client.models.generate_content_stream(
                model=self.model,
                contents=contents,
                config=generate_content_config,  # Tools included in config
            )
            
            # Accumulate response text
            response_text = ""
            # Placeholder for search results
            search_results_data = []
            
            for chunk in stream:
                if chunk.text is not None:
                    response_text += chunk.text
            
            return {
                "response": response_text,
                "search_results": search_results_data  # Currently returns empty list
            }
            
        except Exception as e:
            print(f"Error during Gemini search and generation: {str(e)}")
            # If the tools approach fails, fall back to a simulated search
            try:
                print("Falling back to simulated search...")
                search_prompt = f"""
                I need information about the following research topic:
                
                "{query}"
                
                First, please provide what you know about this topic, focusing on:
                - Recent developments and breakthroughs (2023-2025)
                - Current state-of-the-art approaches
                - Key challenges and limitations
                - Promising future directions
                
                Then, based on this information, please respond to the following request:
                
                {prompt}
                
                Please be specific, factual, and up-to-date in your response.
                """
                
                # Use standard text generation as fallback
                response_text = self.generate_text(
                    search_prompt,
                    temperature=0.2,  # Lower temperature for factual information
                    max_tokens=2000   # Allow for detailed response
                )
                
                return {
                    "response": response_text,
                    "search_results": []
                }
                
            except Exception as e2:
                print(f"Fallback also failed: {str(e2)}")
                return {
                    "response": f"Unable to perform search and generation. Please check your model configuration and API access.",
                    "search_results": []
                }

    def execute_code(self, code: str, inputs: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Simulate Python code execution using Gemini's text generation capabilities.
        NOTE: This does NOT use the dedicated Code Interpreter tool. It asks the LLM
              to predict the output based on the code. May not be accurate for complex code.

        Args:
            code: The Python code string to execute.
            inputs: Optional dictionary of inputs (not directly used in this simulation).

        Returns:
            A dictionary with the simulated result and a success flag.
        """
        prompt = f"Analyze the following Python code and predict its output. Assume standard libraries are available. Respond ONLY with the predicted output (e.g., stdout, return value). Do not include explanations.\n\nCode:\n```python\n{code}\n```"
        if inputs:
            # Note: Inputs aren't truly injected, just mentioned in the prompt
            prompt += f"\n\nAssume the code is run with inputs conceptually similar to: {json.dumps(inputs)}"

        try:
            # Use generate_text to get the simulated output
            # Use low temperature for more deterministic prediction
            simulated_result = self.generate_text(prompt, temperature=0.1, max_tokens=500)

            return {
                "result": simulated_result.strip(),
                "success": True # Flag indicates the API call succeeded, not that the code ran correctly
            }
        except Exception as e:
            print(f"Error during simulated code execution: {str(e)}")
            return {
                "result": f"Execution simulation error: {str(e)}",
                "success": False
            }


class OpenAIClient(LLMClient):
    """Client for OpenAI's API with text and code generation capabilities."""

    def __init__(self, api_key: str = None, model: str = "gpt-4o"): # Using gpt-4o as default
        """
        Initialize the OpenAI client.

        Args:
            api_key: API key for OpenAI. Reads from OPENAI_API_KEY env var if None.
            model: The OpenAI model to use (e.g., "gpt-4o", "gpt-3.5-turbo").
        """
        # Check if the OpenAI library was imported successfully
        if not OpenAI:
            raise ImportError("OpenAI package is not available. Please install it.")

        # Retrieve API key from parameter or environment variable
        api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("API key must be provided or set as OPENAI_API_KEY environment variable")

        super().__init__(api_key=api_key, model=model)

        # Initialize the OpenAI client
        try:
            self.client = OpenAI(api_key=api_key)
            print(f"OpenAIClient initialized with model: {self.model}")
        except Exception as e:
            print(f"Error initializing OpenAI Client: {str(e)}")
            raise ValueError(f"Failed to initialize OpenAI Client: {str(e)}")


    def generate_text(self, prompt: str, temperature: float = 0.7, max_tokens: int = 2048) -> str: # Increased default max_tokens
        """
        Generate text using the OpenAI API.

        Args:
            prompt: The input prompt for text generation.
            temperature: Controls randomness (0.0 to 2.0).
            max_tokens: Maximum number of tokens to generate.

        Returns:
            The generated text as a single string, or an error message.
        """
        try:
            # Use the chat completions endpoint
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens
            )

            # Extract the generated text from the response
            if response.choices and response.choices[0].message:
                 return response.choices[0].message.content.strip()
            else:
                 return "Error: No response generated."

        except Exception as e:
            print(f"Error during OpenAI text generation: {str(e)}")
            # Consider mapping specific OpenAI API errors if needed
            return f"Error generating text: {str(e)}"

    def generate_code(self, specification: str, language: str = "python") -> str:
        """
        Generate code using the OpenAI API.

        Args:
            specification: Detailed description of the code to generate.
            language: The programming language for the code.

        Returns:
            The generated code as a single string, or an error message.
        """
        # System prompt to guide the model towards code generation
        system_prompt = f"You are an expert {language} programmer. Generate clean, efficient, and correct {language} code based ONLY on the provided specification. IMPORTANT: Respond ONLY with the raw code, without any explanations, introductory text, or markdown formatting (like ```python ... ```)."
        user_prompt = f"Specification:\n{specification}"

        try:
            response = self.client.chat.completions.create(
                model=self.model, # Use the configured model
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2, # Lower temperature for code
                max_tokens=3000 # Allow more tokens for potentially complex code
            )

            # Extract the generated code
            if response.choices and response.choices[0].message:
                generated_code = response.choices[0].message.content

                # Basic cleanup: Sometimes models still add markdown fences despite instructions
                generated_code = re.sub(r'^```[a-zA-Z]*\n', '', generated_code) # Remove starting ```lang
                generated_code = re.sub(r'\n```$', '', generated_code) # Remove ending ```
                return generated_code.strip() # Remove leading/trailing whitespace
            else:
                return "Error: No code generated."

        except Exception as e:
            print(f"Error during OpenAI code generation: {str(e)}")
            return f"Error generating code: {str(e)}"

    def search_and_generate(self, query: str, prompt: str) -> Dict[str, Any]:
        """
        Perform search and generate text (Placeholder - Requires external search integration).
        NOTE: Standard OpenAI models (like GPT-4) do not have built-in web search
              like Gemini's tool. This requires integrating a separate search API
              (e.g., Tavily, Google Search API) or using models fine-tuned for search.

        Args:
            query: The search query.
            prompt: The prompt guiding the generation based on search results.

        Returns:
            A dictionary indicating search is not implemented and the original prompt.
        """
        print("Warning: OpenAIClient search_and_generate requires external search integration (not implemented).")
        # Placeholder implementation: Generate text based on the prompt alone without search.
        response_text = self.generate_text(f"Regarding '{query}', please respond to: {prompt}")

        return {
            "response": response_text,
            "search_results": [] # No search performed
        }

