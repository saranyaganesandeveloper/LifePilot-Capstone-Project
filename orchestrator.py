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
    # Handle Query
    # -----------------------------
    def handle(self, user_query, run_meal=True, run_shopping=True, run_travel=True, return_logs=False):

        logs = []
        results = {"meal": "", "shopping": [], "travel": ""}

        # Add memory first
        self.memory.add(user_query)
        memory_context = self.memory.search(user_query, k=5)
        prefs = self.build_preferences()

        # ---- MEAL ----
        meal_text = ""
        if run_meal:
            t0 = time.time()
            meal_text = self.meal_agent.run(user_query, memory_context, prefs)
            t1 = time.time()

            results["meal"] = meal_text
            logs.append({"agent": "MealPlannerAgent", "output": meal_text, "duration": f"{t1-t0:.2f}s"})

        # ---- SHOPPING ----
        if run_shopping:
            t0 = time.time()

            if not meal_text:
                fallback_prompt = f"Generate a vegetarian weekly meal plan based on preferences: {prefs}"
                meal_text = self.meal_agent.run(fallback_prompt, memory_context, prefs)

            shopping = self.shopping_agent.run(meal_text, prefs)

            # LIMIT TO 30 ITEMS
            shopping = shopping[:30]

            t1 = time.time()
            results["shopping"] = shopping
            logs.append({"agent": "ShoppingAgent", "output": shopping[:5], "duration": f"{t1-t0:.2f}s"})

        # ---- TRAVEL ----
        if run_travel:
            t0 = time.time()
            travel = self.travel_agent.run(user_query, memory_context, prefs)
            t1 = time.time()

            results["travel"] = travel
            logs.append({"agent": "TravelAgent", "output": travel, "duration": f"{t1-t0:.2f}s"})

        if return_logs:
            return results, logs

        return results
