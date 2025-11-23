# agents/travel_agent.py
from gen_client import generate

class TravelAgent:
    def run(self, user_query: str, memory: str = ""):
        try:
            prompt = f"""
USER MEMORY:
{memory}

Create a 2-day detailed travel itinerary.
Include:
- Time blocks
- Activities
- Meal suggestions
- Budget per day
- Family-friendly structure

User query: {user_query}
"""
            return generate(prompt)

        except Exception as e:
            return f"[TravelAgent Error] {str(e)}"
