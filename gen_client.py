# gen_client.py

import os
import time
import hashlib
from typing import Dict, List

from google.genai import Client
from dotenv import load_dotenv
load_dotenv()

# ==========================================================
# API KEY HANDLING
# ==========================================================
API_KEY = (
    os.getenv("PRIMARY_GEN_API_KEY")
    or os.getenv("BACKUP_GEN_API_KEY")
    or os.getenv("THIRD_GEN_API_KEY")
)


if not API_KEY:
    raise RuntimeError(
        "❌ No API keys provided. Set PRIMARY_GEN_API_KEY (optionally BACKUP_GEN_API_KEY / THIRD_GEN_API_KEY)."
    )

client = Client(api_key=API_KEY)

# ==========================================================
# MODEL CONFIG
# ==========================================================
PRIMARY_MODEL = "models/gemini-2.5-flash"
FALLBACK_MODELS = [
    "models/gemini-1.5-flash",
    "models/gemini-1.5-flash-8b",
    "models/gemini-1.5-flash-lite",
]

EMBED_MODEL = "models/text-embedding-004"

# ==========================================================
# PERFORMANCE SETTINGS
# ==========================================================
ENABLE_LOGS = False
ENABLE_CACHE = True

_CACHE: Dict[str, str] = {}  # prompt-hash -> output text


def clear_cache():
    """Clear in-memory generation cache (useful for testing)."""
    global _CACHE
    _CACHE = {}


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _extract_text(resp) -> str:
    """Extract text safely from any Gemini response."""
    if not resp:
        return ""

    if hasattr(resp, "text") and resp.text:
        return resp.text

    if hasattr(resp, "candidates") and resp.candidates:
        parts = resp.candidates[0].content.parts
        if parts and hasattr(parts[0], "text"):
            return parts[0].text

    return ""


def _retry_delay(attempt: int) -> float:
    """1, 2, 4, 8 sec backoff."""
    return min(2 ** attempt, 8.0)


def _call_model(model: str, prompt: str) -> str:
    if ENABLE_LOGS:
        print(f"[MODEL CALL] {model}, len={len(prompt)}")

    # Hard trim for safety
    MAX_LEN = 8000
    if len(prompt) > MAX_LEN:
        prompt = prompt[:MAX_LEN]

    resp = client.models.generate_content(
        model=model,
        contents=prompt,
    )
    return _extract_text(resp).strip()


# ==========================================================
# PUBLIC: GENERATE
# ==========================================================
def generate(prompt: str) -> str:
    """
    Robust generation:
      - in-memory cache
      - multiple retries
      - model fallback chain
      - rate-limit backoff
    """

    key = _hash(prompt)
    if ENABLE_CACHE and key in _CACHE:
        if ENABLE_LOGS:
            print("[CACHE HIT]")
        return _CACHE[key]

    models: List[str] = [PRIMARY_MODEL] + FALLBACK_MODELS

    for model in models:
        for attempt in range(3):
            try:
                out = _call_model(model, prompt)
                if out:
                    if ENABLE_CACHE:
                        _CACHE[key] = out
                    return out
                # Empty output → try same model once more
            except Exception as e:
                msg = str(e)
                if "429" in msg or "RESOURCE_EXHAUSTED" in msg:
                    delay = _retry_delay(attempt)
                    if ENABLE_LOGS:
                        print(f"[RATE LIMIT] {model}, retry in {delay}s...")
                    time.sleep(delay)
                    continue
                if ENABLE_LOGS:
                    print(f"[ERROR] {model}: {msg}")
                break  # switch to next model

    # All models failed
    return (
        "❌ All available models failed due to quota or API issues.\n"
        "Please try again later or configure a different API key."
    )


# ==========================================================
# PUBLIC: EMBEDDINGS (robust)
# ==========================================================
def embed(text: str) -> List[float]:
    """
    Robust embedding:
      - retries with backoff on 429
      - returns zero-vector fallback instead of crashing
    """
    if not text:
        return [0.0] * 768

    for attempt in range(3):
        try:
            resp = client.models.embed_content(
                model=EMBED_MODEL,
                contents=text
            )
            if hasattr(resp, "embeddings") and resp.embeddings:
                return resp.embeddings[0].values
        except Exception as e:
            msg = str(e)
            if "429" in msg or "RESOURCE_EXHAUSTED" in msg:
                time.sleep(_retry_delay(attempt))
                continue
            break

    return [0.0] * 768
