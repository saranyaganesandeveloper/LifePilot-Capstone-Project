# utils/validators.py

import re
from typing import Dict, Any

from gen_client import generate


NON_VEG_WORDS = [
    "chicken", "turkey", "egg", "fish", "mutton",
    "beef", "pork", "ham", "bacon", "sausage",
    "shrimp", "tuna", "salmon", "lamb"
]


def _contains_nonveg(text: str) -> bool:
    if not text:
        return False
    pattern = r"\b(" + "|".join(NON_VEG_WORDS) + r")\b"
    return bool(re.search(pattern, text, flags=re.IGNORECASE))


def _safe_lower(val) -> str:
    return val.lower() if isinstance(val, str) else ""


def regenerate_strict_meals(prefs: Dict[str, Any]) -> str:
    """
    Ask the LLM to regenerate a strictly vegetarian plan,
    using the same preferences.
    """
    prompt = f"""
Create a 5-day meal plan STRICTLY following these preferences:
{prefs}

ABSOLUTELY FORBIDDEN:
- Chicken, turkey, fish, eggs, meat, or seafood of any kind.

Only vegetarian meals allowed.

Output ONLY the meal plan as plain text.
No JSON, no bullet symbols, no code fences.
"""
    return generate(prompt).strip()


def validate_meal_plan(text: str, prefs: Dict[str, Any]) -> str:
    """
    Enforce vegetarian / vegan constraints based on prefs.
    If diet_type indicates veg/vegan and the text contains
    non-veg keywords, regenerate once with a strict prompt.
    """

    diet = _safe_lower(prefs.get("diet_type", ""))

    is_strict_veg = any(
        key in diet for key in ["veg", "vegan"]
    )

    if not is_strict_veg:
        # Nothing special to enforce
        return text or ""

    if _contains_nonveg(text or ""):
        # Regenerate a strictly veg plan
        return regenerate_strict_meals(prefs)

    return text or ""
