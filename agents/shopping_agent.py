# agents/shopping_agent.py

import json
import ast
from typing import Any, Dict, List, Union

from gen_client import generate


class ShoppingAgent:
    """
    Takes a meal plan text and produces a structured shopping list
    as a list of dicts: [{category, item, quantity, notes}, ...]
    """

    def _extract_json_array(self, raw: str) -> str:
        """
        Try to extract the first top-level JSON array substring from the raw text.
        """
        raw = raw.strip()
        start = raw.find("[")
        end = raw.rfind("]")
        if start != -1 and end != -1 and end > start:
            return raw[start:end + 1]
        return raw

    def run(
        self,
        meal_plan_text: str,
        prefs: Dict[str, Any]
    ) -> Union[List[Dict[str, Any]], str]:
        """
        Given a meal plan in plain text, return a minimal shopping list
        as a Python list of dicts or a raw string fallback.
        """

        prompt = f"""
You are a grocery list generator.

Given the following meal plan, create a MINIMAL shopping list
(covering required ingredients) with AT MOST 30 items.

Meal plan:
\"\"\"{meal_plan_text}\"\"\"


User preferences (may affect ingredients):
{json.dumps(prefs, indent=2)}

Rules:
- Group items logically into categories (e.g., "Vegetables", "Fruits",
  "Grains & Pulses", "Dairy Alternatives", "Spices", "Staples").
- If the user is lactose intolerant, prefer dairy-free alternatives (e.g. plant milk).
- Return STRICT JSON ONLY.
- DO NOT wrap in backticks.
- Structure: a JSON array of objects, each with keys:
  - "category": string
  - "item": string
  - "quantity": string
  - "notes": string
"""

        raw = generate(prompt).strip()

        # Try strict JSON first
        candidate = self._extract_json_array(raw)

        for attempt in (candidate, candidate.replace("'", '"')):
            try:
                data = json.loads(attempt)
                if isinstance(data, list):
                    return data
            except Exception:
                pass

        # Try Python literal (in case model forgot JSON)
        try:
            data = ast.literal_eval(candidate)
            if isinstance(data, list):
                return data
        except Exception:
            pass

        # Final fallback: return raw string so UI can still display something
        return raw
