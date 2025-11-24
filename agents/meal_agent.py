# agents/meal_agent.py

import re
from typing import Any, Dict, List
from gen_client import generate


class MealPlannerAgent:

    def infer_days(self, query: str) -> int:
        q = (query or "").lower()

        if "tonight" in q:
            return 1

        m = re.search(r"(\d+)\s*[- ]?\s*days?", q)
        if m:
            try:
                return int(m.group(1))
            except:
                pass

        if "weekend" in q:
            return 2
        if "week" in q or "weekly" in q:
            return 7

        return 5

    def run(self, query: str, memory_context: List[str], prefs: Dict[str, Any]) -> str:
        num_days = self.infer_days(query)

        cuisines = ", ".join(prefs.get("cuisines", [])) or "Not specified"
        diet = prefs.get("diet_type") or "Not specified"
        dislikes = ", ".join(prefs.get("dislikes", [])) or "None"
        allergies = ", ".join(prefs.get("allergies", [])) or "None"
        spice = prefs.get("spice_level") or "Not specified"

        context_snippets = "\n".join(memory_context or [])

        if num_days == 1:
            day_info = (
                "Return a short, single vegetarian meal description.\n"
                "Format: 'Tonight: ...'\n"
            )
        else:
            day_info = f"Return a {num_days}-day vegetarian meal plan with Day 1, Day 2, etc."

        prompt = f"""
You are an expert vegetarian meal planner.

User Query:
{query}

Historical context:
{context_snippets}

User Preferences:
- Cuisines: {cuisines}
- Diet type: {diet}
- Dislikes: {dislikes}
- Allergies: {allergies}
- Spice preference: {spice}

Important:
- Vegetarian only.
- Avoid dairy if lactose intolerant.
- No meat, egg, fish, shellfish, poultry.
- Respect dislikes and allergies.

{day_info}

Format:
Plain text only. No JSON. No code fences.
"""

        return generate(prompt).strip()
