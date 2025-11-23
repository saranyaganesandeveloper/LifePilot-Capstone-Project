# gen_client.py
import os
from google import genai
from google.genai.types import GenerateContentResponse

API_KEY = os.getenv("GEN_API_KEY")
client = genai.Client(api_key=API_KEY)

def generate(prompt: str) -> str:
    try:
        response: GenerateContentResponse = client.models.generate_content(
            model="models/gemini-2.5-pro",
            contents=[prompt]
        )
        return response.candidates[0].content.parts[0].text
    except Exception as e:
        return f"[Generation Error] {str(e)}"


def embed(text: str):
    try:
        res = client.models.embed_content(
            model="models/text-embedding-004",
            contents=text
        )
        return res.embeddings[0].values
    except:
        import numpy as np
        return np.random.rand(768).tolist()
