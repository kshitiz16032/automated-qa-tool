from google import genai
from google.genai import types
import os
from dotenv import load_dotenv

load_dotenv()

def get_gemini_response(prompt: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in .env file")
    client = genai.Client(api_key=api_key)
    try:
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                max_output_tokens=8192,
                temperature=0.2,
            )
        )
        return response.text
    except Exception as e:
        print(f"Gemini API error: {e}")
        raise
