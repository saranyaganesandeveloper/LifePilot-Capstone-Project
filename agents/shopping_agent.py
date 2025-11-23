# agents/shopping_agent.py

from gen_client import generate
import json
import re


class ShoppingAgent:
    """
    Converts a meal plan text into a structured JSON shopping list.
    The orchestrator will cap the list to a maximum of 30 items.
    """

    def run(self, meal_text: str, prefs: dict):
        try:
            prompt = f"""
You are a grocery list extraction assistant.

Convert the following MEAL PLAN into a structured JSON shopping list.

Rules:
- Output MUST be a JSON array ONLY.
- No explanatory text before or after JSON.
- No markdown formatting.
- Each item object MUST have:
  - "category" (e.g., Vegetables, Fruits, Grains, Dairy, Spices, Staples, etc.)
  - "item" (product name)
  - "quantity" (e.g., '1 kg', '2 packs', '6 pieces')
  - "notes" (string, may be left "")

Meal plan:
{meal_text}

User preferences (JSON-like):
{prefs}

Return ONLY the JSON array.
Example:

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

            # Extract just the JSON array from the response
            cleaned = re.sub(r"^[^\[]*", "", raw, flags=re.DOTALL)
            cleaned = re.sub(r"[^\]]*$", "", cleaned, flags=re.DOTALL)

            data = json.loads(cleaned)
            return data

        except Exception as e:
            return [{"error": f"[ShoppingAgent Error] {str(e)}"}]
