# agents/meal_agent.py

import re
from typing import Any, Dict, List
from gen_client import generate


class MealPlannerAgent:
    """
    Generates a meal plan in plain text form,
    with number of days inferred from the query.
    """

    def infer_days(self, query: str) -> int:
        q = (query or "").lower()

        # Very short / single meal
        if "tonight" in q or "for tonight" in q:
            return 1
        if "today" in q and ("dinner" in q or "lunch" in q or "breakfast" in q):
            return 1

        # Look for "3 days", "4 day", etc.
        m = re.search(r"(\d+)\s*[- ]?\s*days?", q)
        if m:
            try:
                return max(1, int(m.group(1)))
            except ValueError:
                pass

        # Weekend
        if "weekend" in q:
            return 2

        # Weekly wording
        if "week" in q or "weekly" in q:
            return 7

        # Default
        return 5

    def run(
        self,
        query: str,
        memory_context: List[str],
        prefs: Dict[str, Any]
    ) -> str:
        num_days = self.infer_days(query)

        cuisines = ", ".join(prefs.get("cuisines", [])) or "Not specified"
        diet = prefs.get("diet_type") or "Not specified"
        dislikes = ", ".join(prefs.get("dislikes", [])) or "None"
        allergies = ", ".join(prefs.get("allergies", [])) or "None"
        spice = prefs.get("spice_level") or "Not specified"

        context_snippets = "\n".join(memory_context or [])

        if num_days == 1:
            days_instructions = (
                "The user only needs a single meal (for tonight or one meal).\n"
                "Return just a short, clear description for that meal "
                "(e.g., 'Tonight: ...').\n"
            )
        else:
            days_instructions = (
                f"Return a {num_days}-day meal plan with clear 'Day 1', 'Day 2', etc.\n"
            )

        prompt = f"""
You are an expert meal planner assistant.

User Query:
{query}

User historical context:
{context_snippets}

User preferences (from memory):
- Cuisines: {cuisines}
- Diet type: {diet}
- Dislikes: {dislikes}
- Allergies or intolerances: {allergies}
- Preferred spice level: {spice}

Very important:
- If the user is vegetarian or mentions veg, DO NOT include meat or fish.
- If user is lactose intolerant or dairy is in allergies, avoid milk, yogurt, cheese,
  cream, paneer, butter, ghee, and any milk-based products.
- Respect dislikes and allergies strictly.

{days_instructions}
Format:
- Plain text only.
- No JSON, no code fences.
- You may label meals as Breakfast / Lunch / Dinner if helpful.
"""

        return generate(prompt).strip()
