# agents/shopping_agent.py
from gen_client import generate
import re
from utils.validators import NON_VEG_WORDS

class ShoppingAgent:
    def run(self, meals: str, memory_context: list, prefs: dict):
        try:
            prompt = f"""
Extract a categorized shopping list from this meal plan:

Meal Plan:
{meals}

USER PREFERENCES:
{prefs}

RULES:
- If diet_type = veg, exclude ALL non-veg items.
- Avoid allergies & dislikes.
- Shopping list ONLY.
"""
            raw = generate(prompt)

            # HARD REMOVE any non-veg
            for word in NON_VEG_WORDS:
                raw = re.sub(word, "", raw, flags=re.IGNORECASE)

            # Clean blank lines
            raw = "\n".join([line for line in raw.split("\n") if line.strip()])

            return raw

        except Exception as e:
            return f"[ShoppingAgent Error] {str(e)}"
