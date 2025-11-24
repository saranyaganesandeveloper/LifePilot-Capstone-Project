# ==============================================================
# gen_client.py — Final Production-Stable Version
# ==============================================================

import os
import time
import hashlib
from dotenv import load_dotenv

load_dotenv()  # REQUIRED for .env support

from google.genai import Client


# ==============================================================
# LOAD MULTIPLE API KEYS
# ==============================================================

API_KEYS = [
    os.getenv("PRIMARY_GEN_API_KEY"),
    os.getenv("BACKUP_GEN_API_KEY"),
    os.getenv("THIRD_GEN_API_KEY")
]

API_KEYS = [key for key in API_KEYS if key and key.strip()]

if not API_KEYS:
    raise RuntimeError(
        "❌ No API keys provided. "
        "Set PRIMARY_GEN_API_KEY, BACKUP_GEN_API_KEY, or THIRD_GEN_API_KEY."
    )

_current_key_index = 0
client = Client(api_key=API_KEYS[_current_key_index])


# ==============================================================
# MODEL FALLBACK LISTS
# ==============================================================

TEXT_MODELS = [
    "models/gemini-2.5-flash",
    "models/gemini-1.5-flash",
    "models/gemini-1.5-flash-lite",
    "models/gemini-1.5-flash-8b"
]

EMBED_MODEL = "models/text-embedding-004"


# ==============================================================
# INTERNAL: SWITCH TO NEXT API KEY
# ==============================================================

def _rotate_key():
    global _current_key_index, client

    if _current_key_index < len(API_KEYS) - 1:
        _current_key_index += 1
        client = Client(api_key=API_KEYS[_current_key_index])
        return True
    return False  # No more keys


# ==============================================================
# UTIL — SAFE TEXT EXTRACTION
# ==============================================================

def _extract(resp) -> str:
    if not resp:
        return ""
    if hasattr(resp, "text") and resp.text:
        return resp.text
    if hasattr(resp, "candidates") and resp.candidates:
        parts = resp.candidates[0].content.parts
        if parts and hasattr(parts[0], "text"):
            return parts[0].text
    return ""


# ==============================================================
# INTERNAL: MODEL CALL (ONE MODEL)
# ==============================================================

def _call_model(model: str, prompt: str) -> str:
    try:
        resp = client.models.generate_content(model=model, contents=prompt)
        return _extract(resp)
    except Exception as e:
        return f"[ERROR]{str(e)}"


# ==============================================================
# TEXT GENERATION (FULL FALLBACK ENGINE)
# ==============================================================

def generate(prompt: str) -> str:
    """
    Full production-grade generator.
    Handles:
    - model fallback
    - API key rotation
    - exponential backoff
    - rate limits
    - safe error return
    """

    for model in TEXT_MODELS:
        for attempt in range(3):  # retries
            out = _call_model(model, prompt).strip()

            # success
            if out and not out.startswith("[ERROR]"):
                return out

            # detect quota/rate limit
            if "429" in out or "RESOURCE_EXHAUSTED" in out:
                time.sleep(min(2 ** attempt, 8))
                continue  # retry same model

            # other model-level error → break and use next model
            break

        # model exhausted → rotate API key
        if _rotate_key():
            continue  # retry chain with new key

    # If reached here → all models + all keys failed
    return (
        "❌ **All API keys + model fallbacks exhausted.**\n"
        "You have hit rate-limits across all provided Google API keys.\n"
        "Please wait or add another API key."
    )


# ==============================================================
# EMBEDDINGS (SAFE + RETRY)
# ==============================================================

def embed(text: str):
    """
    Embedding function:
    - retries on rate limit
    - rotates key when needed
    - returns fallback zero-vector if everything fails
    """
    for attempt in range(3):
        try:
            resp = client.models.embed_content(
                model=EMBED_MODEL,
                contents=text
            )
            if hasattr(resp, "embeddings"):
                return resp.embeddings[0].values

        except Exception as e:
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                time.sleep(min(2 ** attempt, 8))
                continue

            # rotate key
            if _rotate_key():
                continue

            break

    # fallback zero-vector → avoids app crash
    return [0.0] * 768
