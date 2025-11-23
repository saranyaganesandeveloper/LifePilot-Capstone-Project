# agents/shopping_agent.py

from gen_client import generate
import json
import re


class ShoppingAgent:

    def run(self, meal_text: str, prefs: dict):
        try:
            prompt = f"""
You are a grocery list extraction assistant.

Convert the following MEAL PLAN into a structured JSON shopping list.

Rules:
- Output MUST be a JSON array ONLY.
- No text before or after JSON.
- No markdown.
- Each item object MUST have:
  - "category"
  - "item"
  - "quantity"
  - "notes" (empty string "")

Meal plan:
{meal_text}

User preferences (JSON-like):
{prefs}

JSON array example:

[
  {{
    "category": "Vegetables",
    "item": "Tomato",
    "quantity": "4",
    "notes": ""
  }},
  {{
    "category": "Grains",
    "item": "Rice",
    "quantity": "1 kg",
    "notes": ""
  }}
]
"""
            raw = generate(prompt)

            # Strip everything outside of the first [...] block
            cleaned = re.sub(r"^[^\[]*", "", raw, flags=re.DOTALL)
            cleaned = re.sub(r"[^\]]*$", "", cleaned, flags=re.DOTALL)

            data = json.loads(cleaned)
            return data

        except Exception as e:
            return [{"error": f"[ShoppingAgent Error] {str(e)}"}]
