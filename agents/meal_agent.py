# agents/meal_agent.py
from gen_client import generate
from utils.validators import validate_meal_plan

class MealPlannerAgent:
    def run(self, user_query: str, memory_context: list, prefs: dict):
        try:
            prompt = f"""
You are a meal planning AI.

USER PREFERENCES:
{prefs}

MEMORY CONTEXT:
{memory_context}

USER REQUEST:
{user_query}

RULES:
- Obey diet_type strictly (veg = NO meat, fish, eggs).
- Respect cuisines, dislikes, allergies.
- Clean 5-day meal plan only.
"""

            raw = generate(prompt)
            validated = validate_meal_plan(raw, prefs)
            return validated

        except Exception as e:
            return f"[MealAgent Error] {str(e)}"
