# agents/shopping_agent.py

import json
import ast
from typing import Any, Dict, List, Union
from gen_client import generate


class ShoppingAgent:

    def _extract_json_array(self, raw: str) -> str:
        raw = raw.strip()
        s = raw.find("[")
        e = raw.rfind("]")
        if s != -1 and e != -1 and e > s:
            return raw[s:e+1]
        return raw

    def run(self, meal_plan_text: str, prefs: Dict[str, Any]) -> Union[List[Dict[str, Any]], str]:

        prompt = f"""
You are a grocery list generator.

Given this meal plan, create a JSON shopping list with AT MOST 30 items.

Meal plan:
\"\"\"{meal_plan_text}\"\"\"


User preferences:
{json.dumps(prefs, indent=2)}

Rules:
- STRICT JSON array.
- Keys: category, item, quantity, notes.
- No markdown. No bullet lists.
"""

        raw = generate(prompt).strip()

        candidate = self._extract_json_array(raw)

        # JSON attempt
        for text in (candidate, candidate.replace("'", '"')):
            try:
                data = json.loads(text)
                if isinstance(data, list):
                    return data
            except:
                pass

        # Python literal fallback
        try:
            data = ast.literal_eval(candidate)
            if isinstance(data, list):
                return data
        except:
            pass

        return raw
