# memory/preference_extractor.py

import json
import re
from typing import Dict, Any

from gen_client import generate


DEFAULT_PREFS = {
    "cuisines": [],
    "diet_type": "",
    "dislikes": [],
    "allergies": [],
    "spice_level": "",
    "travel_style": "",
    "likes": []
}


def extract_preferences(text: str) -> Dict[str, Any]:
    """
    Extracts structured user preferences from a free-text message
    using the LLM, but with strong JSON validation + safe fallback.
    """

    if not text:
        return DEFAULT_PREFS.copy()

    prompt = f"""
You are a system that extracts structured user preferences.

From this text:
\"\"\"{text}\"\"\"


Extract food + travel preferences and return STRICT JSON ONLY:

{{
  "cuisines": [string],
  "diet_type": "veg" | "non-veg" | "vegan" | "" | "lacto-veg" | "ovo-veg",
  "dislikes": [string],
  "allergies": [string],
  "spice_level": "mild" | "medium" | "hot" | "",
  "travel_style": "relaxed" | "adventurous" | "family" | "" | "budget",
  "likes": [string]
}}
"""

    raw = generate(prompt).strip()

    # Try direct JSON
    try:
        data = json.loads(raw)
    except Exception:
        # Try to extract JSON object substring
        try:
            match = re.search(r"\{.*\}", raw, flags=re.DOTALL)
            if match:
                data = json.loads(match.group(0))
            else:
                return DEFAULT_PREFS.copy()
        except Exception:
            return DEFAULT_PREFS.copy()

    out = DEFAULT_PREFS.copy()
    out["cuisines"] = list(data.get("cuisines", []))
    out["diet_type"] = str(data.get("diet_type", "")).strip()
    out["dislikes"] = list(data.get("dislikes", []))
    out["allergies"] = list(data.get("allergies", []))
    out["spice_level"] = str(data.get("spice_level", "")).strip()
    out["travel_style"] = str(data.get("travel_style", "")).strip()
    out["likes"] = list(data.get("likes", []))

    return out
