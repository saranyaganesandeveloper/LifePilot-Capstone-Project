# utils/validators.py

from typing import Dict
import re

from gen_client import generate

NON_VEG_WORDS = [
    "chicken", "turkey", "egg", "eggs", "fish", "mutton",
    "beef", "pork", "ham", "bacon", "sausage",
    "shrimp", "tuna", "salmon", "prawn", "prawns"
]


def contains_nonveg(text: str) -> bool:
    if not text:
        return False
    pattern = r"(" + r"|".join(NON_VEG_WORDS) + r")"
    return bool(re.search(pattern, text, flags=re.IGNORECASE))


def regenerate_strict_meals(prefs: Dict) -> str:
    prompt = f"""
Create a 5-day meal plan STRICTLY following these preferences:
{prefs}

ABSOLUTELY FORBIDDEN:
- Chicken
- Turkey
- Fish
- Eggs
- All meat or seafood

Only vegetarian meals allowed.
Be very strict.

Output ONLY the meal plan as plain text.
"""
    return generate(prompt).strip()


def validate_meal_plan(text: str, prefs: Dict) -> str:
    """
    If the user is veg, enforce vegetarian content.
    """
    diet = (prefs or {}).get("diet_type", "") or ""
    if diet.lower() in {"veg", "vegetarian", "pure veg"}:
        if contains_nonveg(text):
            # regenerate strictly
            return regenerate_strict_meals(prefs)
    return text
