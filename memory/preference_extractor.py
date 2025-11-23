# memory/preference_extractor.py
from gen_client import generate

def extract_preferences(text: str) -> dict:
    prompt = f"""
Extract structured user food preferences from this text.

Text: "{text}"

Return JSON with fields:
- cuisines: list
- diet_type: one of ["veg", "non-veg", "vegan", "none"]
- dislikes: list
- allergies: list
- spice_level: one of ["mild", "medium", "hot", "none"]
"""
    try:
        raw = generate(prompt)
        import json
        return json.loads(raw)
    except:
        return {
            "cuisines": [],
            "diet_type": "none",
            "dislikes": [],
            "allergies": [],
            "spice_level": "none"
        }
