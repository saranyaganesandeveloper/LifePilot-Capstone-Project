# orchestrator.py

import time
import json
from typing import Any, Dict, List, Tuple

from agents.meal_agent import MealPlannerAgent
from agents.shopping_agent import ShoppingAgent
from agents.travel_agent import TravelAgent
from memory.vector_memory import VectorMemory
from memory.preference_extractor import extract_preferences
from utils.validators import validate_meal_plan


class Orchestrator:
    """
    Main coordinator for LifePilot:
    • Stores user queries in memory
    • Extracts preferences
    • Performs deterministic intent detection
    • Runs meal / shopping / travel agents
    """

    def __init__(self) -> None:
        self.meal_agent = MealPlannerAgent()
        self.shopping_agent = ShoppingAgent()
        self.travel_agent = TravelAgent()
        self.memory = VectorMemory()

    # ---------------------------------------------------------
    # DETERMINISTIC INTENT DETECTION (NO LLM)
    # ---------------------------------------------------------
    def detect_intent(self, text: str) -> Dict[str, bool]:
        """
        Pure rule-based intent detection so behavior is consistent
        across all requests and does not depend on LLM randomness.
        """

        if not text:
            return {"meal": False, "shopping": False, "travel": False}

        q = text.lower()

        # --- feature flags ---
        has_trip_words = any(w in q for w in [
            "trip", "travel", "itinerary", "vacation", "visit", "tour",
            "day trip", "weekend in", "weekend trip"
        ])

        has_restaurant_words = any(w in q for w in [
            "restaurant", "restaurants", "cafe", "eatery", "diner", "food spots"
        ])

        # Meal intent only when user is clearly asking for planning meals / recipes
        has_explicit_meal_words = any(w in q for w in [
            "meal plan", "plan my meals", "plan meals", "weekly meals",
            "diet plan", "menu", "breakfast", "lunch", "dinner", "snacks",
            "recipes", "cook for", "cooking plan"
        ])

        has_food_plan_combo = (
            "plan" in q and any(w in q for w in ["meals", "meal", "food", "diet"])
        )

        has_shopping_words = any(w in q for w in [
            "shopping list", "grocery list", "groceries", "grocery",
            "buy ingredients", "market list", "shopping for food"
        ])

        # --- final booleans ---
        travel = has_trip_words or has_restaurant_words
        meal = has_explicit_meal_words or has_food_plan_combo
        shopping = has_shopping_words

        # IMPORTANT: restaurants alone → travel only, not meal
        if has_restaurant_words and not has_explicit_meal_words and not has_shopping_words:
            meal = False
            shopping = False
            travel = True

        return {"meal": meal, "shopping": shopping, "travel": travel}

    # ---------------------------------------------------------
    # EXTRACT USER PREFERENCES FROM MEMORY
    # ---------------------------------------------------------
    def build_preferences(self) -> Dict[str, Any]:
        prefs = {
            "cuisines": set(),
            "diet_type": None,
            "dislikes": set(),
            "allergies": set(),
            "spice_level": None,
            "travel_style": None,
            "likes": set(),
        }

        for txt in getattr(self.memory, "texts", []):
            p = extract_preferences(txt)

            prefs["cuisines"].update(p.get("cuisines", []))
            prefs["dislikes"].update(p.get("dislikes", []))
            prefs["allergies"].update(p.get("allergies", []))
            prefs["likes"].update(p.get("likes", []))

            dt = p.get("diet_type")
            if dt:
                prefs["diet_type"] = dt

            sl = p.get("spice_level")
            if sl:
                prefs["spice_level"] = sl

            ts = p.get("travel_style")
            if ts:
                prefs["travel_style"] = ts

        # Convert sets → lists
        for k in ["cuisines", "dislikes", "allergies", "likes"]:
            prefs[k] = list(prefs[k])

        return prefs

    # ---------------------------------------------------------
    # MAIN HANDLE() METHOD
    # ---------------------------------------------------------
    def handle(
        self,
        user_query: str,
        return_logs: bool = False
    ) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:

        logs: List[Dict[str, Any]] = []
        results: Dict[str, Any] = {"meal": "", "shopping": [], "travel": ""}

        if not user_query:
            return (results, logs) if return_logs else (results, [])

        # Store query in memory
        self.memory.add(user_query)

        prefs = self.build_preferences()

        # Retrieve similar past memory
        try:
            memory_context = self.memory.search(user_query, k=5)
        except Exception:
            memory_context = []

        # ------------------ INTENT DETECTION ------------------
        intents = self.detect_intent(user_query)
        want_meal = intents["meal"]
        want_shopping = intents["shopping"]
        want_travel = intents["travel"]

        # If nothing asked
        if not (want_meal or want_shopping or want_travel):
            logs.append({
                "agent": "Orchestrator",
                "prompt": user_query,
                "output": "No actionable intent detected.",
                "duration": "0.00s",
            })
            return (results, logs) if return_logs else (results, [])

        meal_text = ""

        # ------------------ MEAL PLAN ------------------
        if want_meal:
            t0 = time.time()
            meal_text = self.meal_agent.run(user_query, memory_context, prefs)
            meal_text = validate_meal_plan(meal_text, prefs)
            t1 = time.time()
            results["meal"] = meal_text

            logs.append({
                "agent": "MealPlannerAgent",
                "prompt": user_query,
                "output": meal_text[:900],
                "duration": f"{t1 - t0:.2f}s",
            })

        # ------------------ SHOPPING LIST ------------------
        if want_shopping:
            t0 = time.time()
            # If no meal text yet, create a tiny internal meal description
            if not meal_text:
                fallback_prompt = (
                    "Create a VERY short internal vegetarian meal description for "
                    "2–3 meals, used only to build a grocery list from the user request:\n\n"
                    f"{user_query}\n\n"
                    f"Preferences: {json.dumps(prefs, indent=2)}"
                )
                meal_text = self.meal_agent.run(fallback_prompt, memory_context, prefs)
                meal_text = validate_meal_plan(meal_text, prefs)

            items = self.shopping_agent.run(meal_text, prefs)
            if isinstance(items, list):
                items = items[:30]

            results["shopping"] = items
            t1 = time.time()

            logs.append({
                "agent": "ShoppingAgent",
                "prompt": meal_text[:900],
                "output": str(items)[:900],
                "duration": f"{t1 - t0:.2f}s",
            })

        # ------------------ TRAVEL ITINERARY ------------------
        if want_travel:
            t0 = time.time()
            travel_text = self.travel_agent.run(user_query, memory_context, prefs)
            t1 = time.time()
            results["travel"] = travel_text

            logs.append({
                "agent": "TravelAgent",
                "prompt": user_query,
                "output": travel_text[:900],
                "duration": f"{t1 - t0:.2f}s",
            })

        return (results, logs) if return_logs else (results, [])
