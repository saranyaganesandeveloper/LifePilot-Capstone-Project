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
    Main coordinator for LifePilot.
    - Stores user queries in vector memory.
    - Extracts preferences over time.
    - Auto-detects which agents to call (meal / shopping / travel).
    - Returns a clean dict that the UI can consume.
    """

    def __init__(self) -> None:
        self.meal_agent = MealPlannerAgent()
        self.shopping_agent = ShoppingAgent()
        self.travel_agent = TravelAgent()
        self.memory = VectorMemory()

    # ---------------- Intent detection ----------------
    def detect_intent(self, text: str) -> Dict[str, bool]:
        """
        Very simple keyword-based intent detection.
        """
        t = (text or "").lower()

        meal_words = [
            "meal", "diet", "breakfast", "lunch", "dinner",
            "menu", "food plan", "meal plan", "weekly meals",
            "snacks", "cooking plan"
        ]
        shopping_words = [
            "shopping", "grocery", "groceries", "shopping list",
            "buy ingredients", "ingredients list", "market list"
        ]
        travel_words = [
            "travel", "trip", "itinerary", "vacation", "tour",
            "road trip", "day trip", "visit", "2 days", "3 days",
            "4 days", "5 days", "weekend", "holiday"
        ]

        has_meal = any(w in t for w in meal_words)
        has_shopping = any(w in t for w in shopping_words)
        has_travel = any(w in t for w in travel_words)

        return {
            "meal": has_meal,
            "shopping": has_shopping,
            "travel": has_travel,
        }

    # ---------------- Preferences from memory ----------------
    def build_preferences(self) -> Dict[str, Any]:
        """
        Aggregate user food preferences from memory.texts using preference_extractor.
        """
        prefs = {
            "cuisines": set(),
            "diet_type": None,
            "dislikes": set(),
            "allergies": set(),
            "spice_level": None,
            "travel_style": None,
            "likes": set(),
        }

        # VectorMemory is assumed to store raw texts in self.texts
        for txt in getattr(self.memory, "texts", []):
            p = extract_preferences(txt)

            prefs["cuisines"].update(p.get("cuisines", []))
            prefs["dislikes"].update(p.get("dislikes", []))
            prefs["allergies"].update(p.get("allergies", []))
            prefs["likes"].update(p.get("likes", []))

            dt = p.get("diet_type")
            if dt and dt.lower() != "none":
                prefs["diet_type"] = dt

            sl = p.get("spice_level")
            if sl and sl.lower() != "none":
                prefs["spice_level"] = sl

            ts = p.get("travel_style")
            if ts and ts.lower() != "none":
                prefs["travel_style"] = ts

        # Convert sets to lists for JSON safety
        prefs["cuisines"] = list(prefs["cuisines"])
        prefs["dislikes"] = list(prefs["dislikes"])
        prefs["allergies"] = list(prefs["allergies"])
        prefs["likes"] = list(prefs["likes"])

        return prefs

    # ---------------- Main entry point ----------------
    def handle(
        self,
        user_query: str,
        return_logs: bool = False
    ) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Auto-detects which agents to run. No UI agent selection.
        Returns:
            results = {
                "meal": str,
                "shopping": list | str,
                "travel": str
            }
            logs = list of debug dicts (if return_logs=True)
        """
        logs: List[Dict[str, Any]] = []
        results: Dict[str, Any] = {"meal": "", "shopping": [], "travel": ""}

        if not user_query:
            if return_logs:
                return results, logs
            return results, []

        # Always store the query in memory
        self.memory.add(user_query)

        # Build preference summary
        prefs = self.build_preferences()

        # Try to get some similar past context (optional)
        try:
            memory_context = self.memory.search(user_query, k=5)
        except Exception:
            memory_context = []

        # Detect intent
        intents = self.detect_intent(user_query)
        want_meal = intents["meal"]
        want_shopping = intents["shopping"]
        want_travel = intents["travel"]

        # If user is just expressing preferences (no explicit request)
        if not (want_meal or want_shopping or want_travel):
            msg = "Only memory updated; no agents triggered."
            logs.append({
                "agent": "Orchestrator",
                "prompt": user_query,
                "output": msg,
                "duration": "0.00s",
            })
            if return_logs:
                return results, logs
            return results, []

        meal_text = ""

        # -------- MEAL PLAN --------
        if want_meal:
            t0 = time.time()
            meal_text = self.meal_agent.run(user_query, memory_context, prefs)
            # Enforce vegetarian if needed
            meal_text = validate_meal_plan(meal_text, prefs)
            t1 = time.time()

            results["meal"] = meal_text
            logs.append({
                "agent": "MealPlannerAgent",
                "prompt": user_query,
                "output": str(meal_text)[:900],
                "duration": f"{t1 - t0:.2f}s",
            })

        # -------- SHOPPING LIST --------
        if want_shopping:
            t0 = time.time()

            # If user asked ONLY shopping, generate a minimal internal meal basis
            if not meal_text:
                fallback_prompt = (
                    "Generate a simple, short meal description from this request "
                    "and preferences. This is only used internally to build "
                    "a shopping list.\n\n"
                    f"Request: {user_query}\n\n"
                    f"Preferences: {json.dumps(prefs, indent=2)}"
                )
                meal_text = self.meal_agent.run(
                    fallback_prompt, memory_context, prefs
                )
                meal_text = validate_meal_plan(meal_text, prefs)
                logs.append({
                    "agent": "MealPlannerAgent (fallback-for-shopping)",
                    "prompt": fallback_prompt,
                    "output": str(meal_text)[:900],
                    "duration": "N/A",
                })

            shopping_items = self.shopping_agent.run(meal_text, prefs)

            if isinstance(shopping_items, list):
                shopping_items = shopping_items[:30]  # max 30 items
            results["shopping"] = shopping_items

            t1 = time.time()
            logs.append({
                "agent": "ShoppingAgent",
                "prompt": str(meal_text)[:900],
                "output": str(shopping_items)[:900],
                "duration": f"{t1 - t0:.2f}s",
            })

        # -------- TRAVEL ITINERARY --------
        if want_travel:
            t0 = time.time()
            travel_text = self.travel_agent.run(user_query, memory_context, prefs)
            t1 = time.time()
            results["travel"] = travel_text
            logs.append({
                "agent": "TravelAgent",
                "prompt": user_query,
                "output": str(travel_text)[:900],
                "duration": f"{t1 - t0:.2f}s",
            })

        if return_logs:
            return results, logs
        return results, []
