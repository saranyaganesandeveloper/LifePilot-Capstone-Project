# agents/meal_agent.py

from gen_client import generate


class MealPlannerAgent:
    """
    Generates a weekly meal plan using:
    - current user query
    - vector memory context
    - dynamic preferences (cuisines, diet_type, spice_level, etc.)
    """

    def run(self, user_query: str, memory_context: list, prefs: dict) -> str:
        try:
            prompt = f"""
You are a professional meal planner.

Task:
Generate a clear weekly meal plan ONLY.
Do NOT include shopping lists.
Do NOT include travel content.

User preferences (JSON-like):
{prefs}

Relevant past context:
{memory_context}

User request:
{user_query}

Guidelines:
- Respect diet_type (veg / non-veg / vegan) if present.
- Respect cuisines and dislikes.
- Use a 5–7 day structure.
- For each day, suggest Breakfast, Lunch, and Dinner.

Return ONLY the meal plan as plain text, for example:

Day 1:
  Breakfast - ...
  Lunch - ...
  Dinner - ...

Day 2:
  Breakfast - ...
  Lunch - ...
  Dinner - ...
"""
            return generate(prompt)
        except Exception as e:
            return f"[MealPlannerAgent Error] {str(e)}"
