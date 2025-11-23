# utils/validators.py
from gen_client import generate
import re

NON_VEG_WORDS = [
    "chicken", "turkey", "egg", "fish", "mutton",
    "beef", "pork", "ham", "bacon", "sausage", 
    "shrimp", "tuna", "salmon"
]

def contains_nonveg(text: str) -> bool:
    pattern = r"|".join(NON_VEG_WORDS)
    return bool(re.search(pattern, text, flags=re.IGNORECASE))


def regenerate_strict_meals(prefs):
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

Output ONLY the meal plan.
"""
    return generate(prompt)


def validate_meal_plan(text: str, prefs: dict):
    # If diet is veg → enforce vegetarian
    if prefs.get("diet_type") == "veg":
        if contains_nonveg(text):
            # regenerate strictly
            return regenerate_strict_meals(prefs)

    return text
