# agents/meal_agent.py

import re
from typing import Any, Dict, List

from gen_client import generate


class MealPlannerAgent:
    """
    Generates a plain-text meal plan.
    Infers number of days from the query.
    """

    def infer_days(self, query: str) -> int:
        q = (query or "").lower()

        # Very short / single-meal requests
        if "tonight" in q or "for tonight" in q:
            return 1
        if "today" in q and any(w in q for w in ["breakfast", "lunch", "dinner"]):
            return 1

        # Numeric patterns: "3 days", "4-day", etc.
        m = re.search(r"(\d+)\s*[- ]?\s*days?", q)
        if m:
            try:
                n = int(m.group(1))
                return max(1, min(n, 10))
            except Exception:
                pass

        # Week / weekly → 7 days
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
                "Return just a short, clear description for that meal.\n"
            )
        else:
            days_instructions = f"Return a {num_days}-day meal plan with clear 'Day 1', 'Day 2', etc.\n"

        prompt = f"""
You are an expert vegetarian-friendly meal planner.

User Query:
{query}

User historical context:
{context_snippets}

User preferences:
- Cuisines: {cuisines}
- Diet type: {diet}
- Dislikes: {dislikes}
- Allergies or intolerances: {allergies}
- Preferred spice level: {spice}

Rules:
- If the user is vegetarian or mentions veg, DO NOT include any meat or fish.
- If user is lactose intolerant or dairy is in allergies, avoid milk, yogurt, cheese,
  cream, paneer, butter, ghee, and all milk-based products.
- Respect dislikes and allergies strictly.

{days_instructions}
Format:
- Plain text only.
- No JSON, no code fences.
- You may label meals as Breakfast / Lunch / Dinner if helpful.
"""

        return generate(prompt).strip()
