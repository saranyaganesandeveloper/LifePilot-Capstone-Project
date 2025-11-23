# gen_client.py

import os
from google.genai import Client

API_KEY = os.getenv("GEN_API_KEY")

client = Client(api_key=API_KEY)

GEN_MODEL = "models/gemini-2.5-flash"
EMBED_MODEL = "models/text-embedding-004"


# ---------------------------------------------------------
# TEXT GENERATION  (google-genai v1.52.0)
# ---------------------------------------------------------
def generate(prompt: str) -> str:
    try:
        # NO generation_config allowed
        resp = client.models.generate_content(
            model=GEN_MODEL,
            contents=prompt
        )

        # Standard output path
        if hasattr(resp, "text") and resp.text:
            return resp.text

        # Candidate fallback (rare)
        if hasattr(resp, "candidates") and resp.candidates:
            parts = resp.candidates[0].content.parts
            if parts and hasattr(parts[0], "text"):
                return parts[0].text

        return ""

    except Exception as e:
        return f"[Generation Error] {str(e)}"


# ---------------------------------------------------------
# EMBEDDINGS  (google-genai v1.52.0)
# ---------------------------------------------------------
def embed(text: str):
    try:
        resp = client.models.embed_content(
            model=EMBED_MODEL,
            contents=text     # correct for your SDK
        )

        # New API format:
        if hasattr(resp, "embeddings"):
            return resp.embeddings[0].values

        return [0.0] * 768

    except Exception as e:
        print("Embed Error:", e)
        return [0.0] * 768
