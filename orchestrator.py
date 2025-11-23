# orchestrator.py
from agents.meal_agent import MealPlannerAgent
from agents.shopping_agent import ShoppingAgent
from agents.travel_agent import TravelAgent
from memory.vector_memory import VectorMemory
from memory.preference_extractor import extract_preferences

class Orchestrator:
    def __init__(self):
        self.meals = MealPlannerAgent()
        self.shop = ShoppingAgent()
        self.travel = TravelAgent()
        self.memory = VectorMemory()

        # structured preference store
        self.user_prefs = {
            "cuisines": [],
            "diet_type": "none",
            "dislikes": [],
            "allergies": [],
            "spice_level": "none"
        }

    def update_prefs(self, text: str):
        prefs = extract_preferences(text)
        # merge lists
        self.user_prefs["cuisines"] = list(set(self.user_prefs["cuisines"] + prefs["cuisines"]))
        self.user_prefs["dislikes"] = list(set(self.user_prefs["dislikes"] + prefs["dislikes"]))
        self.user_prefs["allergies"] = list(set(self.user_prefs["allergies"] + prefs["allergies"]))

        # override diet + spice_level only if detected
        if prefs["diet_type"] != "none":
            self.user_prefs["diet_type"] = prefs["diet_type"]

        if prefs["spice_level"] != "none":
            self.user_prefs["spice_level"] = prefs["spice_level"]

    def handle(self, user_query: str):
        q = user_query.lower().strip()

        # save the message
        self.memory.add(user_query)
        
        # update structured preferences
        self.update_prefs(user_query)

        # vector memory context
        vector_context = self.memory.search(user_query)

        try:
            if "meal" in q and "shop" not in q:
                return self.meals.run(user_query, vector_context, self.user_prefs)

            elif "shop" in q or "shopping" in q:
                plan = self.meals.run("weekly meal plan", vector_context, self.user_prefs)
                return self.shop.run(plan, vector_context, self.user_prefs)

            elif "travel" in q or "trip" in q:
                return self.travel.run(user_query, vector_context, self.user_prefs)

            return "I can help with meals, shopping lists, travel, and more."

        except Exception as e:
            return f"[Orchestrator Error] {str(e)}"
