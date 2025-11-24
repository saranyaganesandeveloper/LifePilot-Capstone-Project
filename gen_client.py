# gen_client.py

import os
from typing import List

from google.genai import Client

API_KEY = os.getenv("GEN_API_KEY")

if not API_KEY:
    # Fail fast so user notices env issue instead of silent failures
    raise RuntimeError(
        "GEN_API_KEY environment variable is not set. "
        "Export it before running LifePilot."
    )

client = Client(api_key=API_KEY)

GEN_MODEL = "models/gemini-2.5-flash"
EMBED_MODEL = "models/text-embedding-004"


# ---------------------------------------------------------
# TEXT GENERATION (google-genai v1.52.0)
# ---------------------------------------------------------
def generate(prompt: str) -> str:
    try:
        resp = client.models.generate_content(
            model=GEN_MODEL,
            contents=prompt,
        )

        # Standard output
        if hasattr(resp, "text") and resp.text:
            return resp.text

        # Candidate fallback (rare)
        if getattr(resp, "candidates", None):
            parts = resp.candidates[0].content.parts
            if parts and hasattr(parts[0], "text"):
                return parts[0].text

        return ""

    except Exception as e:
        return f"[Generation Error] {str(e)}"


# ---------------------------------------------------------
# EMBEDDINGS (google-genai v1.52.0)
# ---------------------------------------------------------
def embed(text: str) -> List[float]:
    try:
        resp = client.models.embed_content(
            model=EMBED_MODEL,
            contents=text,
        )

        if hasattr(resp, "embeddings") and resp.embeddings:
            return list(resp.embeddings[0].values)

        return [0.0] * 768

    except Exception as e:
        print("Embed Error:", e)
        return [0.0] * 768
