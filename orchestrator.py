# orchestrator.py

import time
from agents.meal_agent import MealPlannerAgent
from agents.shopping_agent import ShoppingAgent
from agents.travel_agent import TravelAgent
from memory.vector_memory import VectorMemory
from memory.preference_extractor import extract_preferences


class Orchestrator:

    def __init__(self):
        self.meal_agent = MealPlannerAgent()
        self.shopping_agent = ShoppingAgent()
        self.travel_agent = TravelAgent()
        self.memory = VectorMemory()

    # -----------------------------
    # Build dynamic preferences
    # -----------------------------
    def build_preferences(self):
        """
        Aggregate preferences from all memory entries using your
        existing memory/preference_extractor.py.
        """

        prefs = {
            "cuisines": set(),
            "diet_type": None,
            "dislikes": set(),
            "allergies": set(),
            "spice_level": None,
        }

        for entry in self.memory.texts:
            p = extract_preferences(entry)

            prefs["cuisines"].update(p.get("cuisines", []))
            prefs["dislikes"].update(p.get("dislikes", []))
            prefs["allergies"].update(p.get("allergies", []))

            dt = p.get("diet_type")
            if dt and dt != "none":
                prefs["diet_type"] = dt

            sl = p.get("spice_level")
            if sl and sl != "none":
                prefs["spice_level"] = sl

        prefs["cuisines"] = list(prefs["cuisines"])
        prefs["dislikes"] = list(prefs["dislikes"])
        prefs["allergies"] = list(prefs["allergies"])

        return prefs

    # -----------------------------
    # Main entry used by UI
    # -----------------------------
    def handle(
        self,
        user_query: str,
        run_meal: bool = True,
        run_shopping: bool = True,
        run_travel: bool = True,
        return_logs: bool = False,
    ):
        results = {"meal": "", "shopping": [], "travel": ""}
        logs = []

        # Save query into memory
        self.memory.add(user_query)

        # Vector memory for context
        memory_context = self.memory.search(user_query, k=5)
        # Dynamic prefs from all past messages
        prefs = self.build_preferences()

        # --------- MEAL PLAN ----------
        meal_text = ""
        if run_meal:
            t0 = time.time()
            meal_text = self.meal_agent.run(user_query, memory_context, prefs)
            t1 = time.time()

            results["meal"] = meal_text
            logs.append(
                {
                    "agent": "MealPlannerAgent",
                    "prompt": user_query,
                    "output": str(meal_text)[:500],
                    "duration": f"{t1 - t0:.2f}s",
                }
            )

        # --------- SHOPPING LIST ----------
        if run_shopping:
            t0 = time.time()

            # If user only selected Shopping (no meal),
            # we still need a meal plan to base the list on.
            if not meal_text:
                # Fallback meal plan just for shopping generation
                fallback_prompt = (
                    f"Generate a simple 5–7 day meal plan based on "
                    f"this user request and preferences.\n\n"
                    f"Request: {user_query}\n\nPreferences: {prefs}"
                )
                meal_for_shopping = self.meal_agent.run(
                    fallback_prompt, memory_context, prefs
                )
            else:
                meal_for_shopping = meal_text

            shopping = self.shopping_agent.run(meal_for_shopping, prefs)
            t1 = time.time()

            results["shopping"] = shopping
            logs.append(
                {
                    "agent": "ShoppingAgent",
                    "prompt": meal_for_shopping[:500],
                    "output": str(shopping)[:500],
                    "duration": f"{t1 - t0:.2f}s",
                }
            )

        # --------- TRAVEL ITINERARY ----------
        if run_travel:
            t0 = time.time()
            travel_text = self.travel_agent.run(user_query, memory_context, prefs)
            t1 = time.time()

            results["travel"] = travel_text
            logs.append(
                {
                    "agent": "TravelAgent",
                    "prompt": user_query,
                    "output": str(travel_text)[:500],
                    "duration": f"{t1 - t0:.2f}s",
                }
            )

        if return_logs:
            return results, logs
        return results
