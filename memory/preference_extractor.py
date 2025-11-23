# memory/preference_extractor.py
from gen_client import generate
import json
import re

def extract_preferences(text: str) -> dict:
    prompt = f"""
You are a system that extracts structured user preferences.

Extract food + travel preferences from this text:

"{text}"

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
        # Strip everything before/after JSON
        cleaned = re.sub(r"^[^{]*", "", raw)
        cleaned = re.sub(r"[^}]*$", "", cleaned)

        return json.loads(cleaned)

    except:
        return {
            "cuisines": [],
            "diet_type": "",
            "dislikes": [],
            "allergies": [],
            "spice_level": "",
            "travel_style": "",
            "likes": []
        }
