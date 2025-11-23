# agents/meal_agent.py

from gen_client import generate


class MealPlannerAgent:

    def run(self, user_query: str, memory_context: list, prefs: dict):
        try:
            prompt = f"""
You are a professional meal planner.

Task:
Generate a clean weekly meal plan ONLY.
Do NOT include shopping lists.
Do NOT include travel plans.

User preferences (JSON-like):
{prefs}

Relevant memory:
{memory_context}

User request:
{user_query}

Return ONLY the meal plan as text in a simple readable format, e.g.:

Day 1: Breakfast - ...
       Lunch - ...
       Dinner - ...

Day 2: ...
"""
            return generate(prompt)
        except Exception as e:
            return f"[MealPlannerAgent Error] {str(e)}"
