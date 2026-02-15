import os
from dotenv import load_dotenv
load_dotenv()

from google import genai

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY not set")

client = genai.Client(api_key=API_KEY)

def embed_text(text: str):
    response = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text
    )

    # New SDK returns:
    # response.embeddings[0].values
    return response.embeddings[0].values
