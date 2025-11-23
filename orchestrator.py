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

    # -----------------------------------------------------
    # Simple intent detection (no extra API calls)
    # -----------------------------------------------------
    def detect_intent(self, text: str) -> dict:
        """
        Heuristic intent detection based on keywords in the user query.

        Returns:
            {
              "meal": bool,
              "shopping": bool,
              "travel": bool
            }
        """
        t = (text or "").lower()

        meal_words = [
            "meal plan", "meals", "diet plan", "breakfast", "lunch",
            "dinner", "menu", "weekly meals", "mealprep", "meal prep"
        ]
        shopping_words = [
            "shopping", "shopping list", "grocery", "groceries",
            "grocery list", "ingredients list", "buy ingredients", "buy groceries"
        ]
        travel_words = [
            "travel", "trip", "itinerary", "vacation", "visit",
            "day trip", "tour", "2 days", "3 days", "weekend trip"
        ]

        has_meal = any(w in t for w in meal_words)
        has_shopping = any(w in t for w in shopping_words)
        has_travel = any(w in t for w in travel_words)

        return {
            "meal": has_meal,
            "shopping": has_shopping,
            "travel": has_travel,
        }

    # -----------------------------------------------------
    # Build dynamic preferences from memory
    # -----------------------------------------------------
    def build_preferences(self) -> dict:
        """
        Aggregate user preferences from all stored memory texts using
        your preference_extractor.py.
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

    # -----------------------------------------------------
    # Main entrypoint called by the UI
    # -----------------------------------------------------
    def handle(
        self,
        user_query: str,
        run_meal: bool = True,
        run_shopping: bool = True,
        run_travel: bool = True,
        return_logs: bool = False,
    ):
        """
        Orchestrate which agents to run based on:
        - UI toggles (run_meal, run_shopping, run_travel)
        - Detected intents in the user_query
        - Memory + dynamic preferences

        Returns:
            results = {
                "meal": str,
                "shopping": list,
                "travel": str
            }
            logs = [ {agent, prompt, output, duration}, ... ] if return_logs=True
        """
        logs = []
        results = {"meal": "", "shopping": [], "travel": ""}

        # 1) Always store query in memory
        self.memory.add(user_query)

        # 2) Build prefs + retrieve relevant memory context
        prefs = self.build_preferences()
        memory_context = self.memory.search(user_query, k=5)

        # 3) Detect intent from the text
        intents = self.detect_intent(user_query)

        # Combine UI toggles + intent detection
        want_meal = run_meal and intents["meal"]
        want_shopping = run_shopping and intents["shopping"]
        want_travel = run_travel and intents["travel"]

        # If user is just expressing preferences (like
        # "I love South Indian vegetarian food") and not
        # explicitly asking for a plan/list/trip, no agent runs.
        if not (want_meal or want_shopping or want_travel):
            if return_logs:
                logs.append(
                    {
                        "agent": "Orchestrator",
                        "prompt": user_query,
                        "output": "No agents triggered (only memory/preferences updated).",
                        "duration": "0.00s",
                    }
                )
                return results, logs
            return results

        # ---------------------------------
        # MEAL PLAN
        # ---------------------------------
        meal_text = ""
        if want_meal:
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

        # ---------------------------------
        # SHOPPING LIST
        # ---------------------------------
        if want_shopping:
            t0 = time.time()

            # If user didn't explicitly ask for a meal but only shopping,
            # we still need a meal plan as a base → auto-generate fallback.
            if not meal_text:
                fallback_prompt = (
                    f"Generate a simple weekly meal plan based on this request "
                    f"and preferences.\n\nRequest: {user_query}\n\nPreferences: {prefs}"
                )
                meal_text = self.meal_agent.run(fallback_prompt, memory_context, prefs)
                logs.append(
                    {
                        "agent": "MealPlannerAgent (fallback-for-shopping)",
                        "prompt": fallback_prompt,
                        "output": str(meal_text)[:500],
                        "duration": "N/A",
                    }
                )

            shopping_list = self.shopping_agent.run(meal_text, prefs)
            # Enforce max 30 items
            if isinstance(shopping_list, list):
                shopping_list = shopping_list[:30]

            t1 = time.time()
            results["shopping"] = shopping_list
            logs.append(
                {
                    "agent": "ShoppingAgent",
                    "prompt": str(meal_text)[:500],
                    "output": str(shopping_list)[:500],
                    "duration": f"{t1 - t0:.2f}s",
                }
            )

        # ---------------------------------
        # TRAVEL ITINERARY
        # ---------------------------------
        if want_travel:
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
