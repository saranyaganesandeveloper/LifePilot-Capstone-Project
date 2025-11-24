# memory/preference_extractor.py

import json
import re
from typing import Dict, Any
from gen_client import generate

PREF_SCHEMA = {
    "cuisines": list,
    "diet_type": str,
    "dislikes": list,
    "allergies": list,
    "spice_level": str,
    "travel_style": str,
    "likes": list,
}

DEFAULT_PREFS: Dict[str, Any] = {
    "cuisines": [],
    "diet_type": "",
    "dislikes": [],
    "allergies": [],
    "spice_level": "",
    "travel_style": "",
    "likes": [],
}


def _extract_json_structure(raw: str) -> Dict[str, Any] | None:
    """
    Extract the FIRST valid {...} JSON block from raw text.
    Cleans up common LLM mistakes:
      - extra text before/after JSON
      - True/False/None vs true/false/null
      - trailing commas
    """
    try:
        match = re.search(r"\{[\s\S]*\}", raw)
        if not match:
            return None

        text = match.group(0).strip()

        # Normalize JS/Python differences
        text = text.replace("True", "true")
        text = text.replace("False", "false")
        text = text.replace("None", "null")

        # Remove trailing commas before } or ]
        text = re.sub(r",\s*([}\]])", r"\1", text)

        return json.loads(text)
    except Exception:
        return None


def _canonical_diet_type(raw_value: str) -> str:
    """
    Map various LLM outputs into a small canonical set.
    Currently:
      - "veg", "vegetarian", "plant-based" -> "veg"
      - "vegan" -> "vegan"
      - others -> ""
    """
    if not raw_value:
        return ""

    v = raw_value.strip().lower()
    if any(x in v for x in ["veg", "vegetarian", "plant based", "plant-based"]):
        return "veg"
    if "vegan" in v:
        return "vegan"

    # For now we only use vegetarian/vegan vs empty
    return ""


def _validate_preferences(parsed: Dict[str, Any]) -> Dict[str, Any]:
    """
    Guarantee the final dict matches DEFAULT_PREFS schema exactly.
    Missing or invalid fields get replaced with defaults.
    Wrong types get sanitized.
    """
    final = DEFAULT_PREFS.copy()

    for key, expected_type in PREF_SCHEMA.items():
        val = parsed.get(key, None)

        # If missing → default
        if val is None:
            final[key] = DEFAULT_PREFS[key]
            continue

        if expected_type == list:
            if isinstance(val, list):
                final[key] = [str(v).strip() for v in val]
            else:
                final[key] = [str(val).strip()]
        else:
            final[key] = str(val).strip()

    # Canonicalize diet_type specifically
    final["diet_type"] = _canonical_diet_type(final.get("diet_type", ""))

    return final


def extract_preferences(text: str) -> Dict[str, Any]:
    """
    MAIN ENTRY:
    Robust & reliable preference extraction using LLM + validation.
    """

    prompt = f"""
Extract strict structured preference JSON from the following user text:

\"\"\"{text}\"\"\"

Return ONLY the following JSON schema and nothing else:

{{
  "cuisines": [],
  "diet_type": "",
  "dislikes": [],
  "allergies": [],
  "spice_level": "",
  "travel_style": "",
  "likes": []
}}

Rules:
- JSON ONLY.
- No comments, no explanations, no markdown.
- If unsure, keep fields empty ("" or []).
"""

    raw = generate(prompt)

    parsed = _extract_json_structure(raw)
    if not parsed:
        return DEFAULT_PREFS.copy()

    return _validate_preferences(parsed)
