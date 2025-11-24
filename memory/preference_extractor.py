# memory/preference_extractor.py

import json
import re
from typing import Dict, Any

from gen_client import generate


def extract_preferences(text: str) -> Dict[str, Any]:
    """
    Ask the model to summarize user preferences from free text.
    Returns a stable dict, even if parsing fails.
    """
    prompt = f"""
You are a system that extracts structured user preferences.

Extract food + travel preferences from this text:

\"\"\"{text}\"\"\"


Return STRICT JSON ONLY with this structure:

{{
  "cuisines": [],
  "diet_type": "",
  "dislikes": [],
  "allergies": [],
  "spice_level": "",
  "travel_style": "",
  "likes": []
}}
"""

    raw = generate(prompt)

    try:
        # Try to strip everything before first '{' and after last '}'
        cleaned = re.sub(r"^[^{]*", "", raw)
        cleaned = re.sub(r"[^}]*$", "", cleaned)

        data = json.loads(cleaned)

        # Fill defaults if keys missing
        return {
            "cuisines": data.get("cuisines", []) or [],
            "diet_type": data.get("diet_type", "") or "",
            "dislikes": data.get("dislikes", []) or [],
            "allergies": data.get("allergies", []) or [],
            "spice_level": data.get("spice_level", "") or "",
            "travel_style": data.get("travel_style", "") or "",
            "likes": data.get("likes", []) or [],
        }

    except Exception:
        return {
            "cuisines": [],
            "diet_type": "",
            "dislikes": [],
            "allergies": [],
            "spice_level": "",
            "travel_style": "",
            "likes": [],
        }
