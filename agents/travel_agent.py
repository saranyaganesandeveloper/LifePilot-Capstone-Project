# agents/travel_agent.py

import re
from typing import Any, Dict, List
from gen_client import generate


class TravelAgent:
    """
    Builds a multi-day travel itinerary in plain text.
    """
    NUMBER_WORDS = {
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
        "six": 6,
        "seven": 7,
        "eight": 8,
        "nine": 9,
        "ten": 10,
    }

    def infer_days(self, query: str) -> int:
        """
        Extracts the number of travel days reliably using:
        • numeric patterns: "2 days", "3-day", "for 4 days"
        • word patterns: "two days", "three-day trip"
        • fallback: weekend = 2 days
        • fallback default = 1 day (short trip)
        """

        if not query:
            return 1

        q = query.lower().strip()

        # ----------------------------------------------
        # 1. Look for explicit numeric patterns
        # ----------------------------------------------
        numeric_match = re.search(r"(\d+)\s*[- ]?\s*day", q)
        if numeric_match:
            try:
                days = int(numeric_match.group(1))
                if days >= 1:
                    return days
            except:
                pass

        # ----------------------------------------------
        # 2. Look for spelled-out numbers ("two-day trip")
        # ----------------------------------------------
        for word, num in self.NUMBER_WORDS.items():
            if re.search(rf"{word}\s*[- ]?\s*day", q):
                return num

            if re.search(rf"{word}\s+days", q):
                return num

        # ----------------------------------------------
        # 3. Weekend logic → always 2 days
        # ----------------------------------------------
        if "weekend" in q:
            return 2

        # ----------------------------------------------
        # 4. Overnight trip = 1 day
        # ----------------------------------------------
        if "overnight" in q:
            return 1

        # ----------------------------------------------
        # 5. Words implying a short single-day trip
        # ----------------------------------------------
        one_day_triggers = ["quick trip", "short trip", "day trip", "tomorrow"]
        if any(w in q for w in one_day_triggers):
            return 1

        # ----------------------------------------------
        # 6. Default fallback: 2 days for general trips
        # ----------------------------------------------
        if "trip" in q or "travel" in q or "visit" in q:
            return 2

        # ----------------------------------------------
        # 7. Absolute fallback
        # ----------------------------------------------
        return 1

    def run(
        self,
        query: str,
        memory_context: List[str],
        prefs: Dict[str, Any]
    ) -> str:
        num_days = self.infer_days(query)

        cuisines = ", ".join(prefs.get("cuisines", [])) or "Not specified"
        diet = prefs.get("diet_type") or "Not specified"
        allergies = ", ".join(prefs.get("allergies", [])) or "None"
        travel_style = prefs.get("travel_style") or "Not specified"

        context_snippets = "\n".join(memory_context or [])

        prompt = f"""
You are a friendly but precise travel planner.

User Query:
{query}

User historical context:
{context_snippets}

User food preferences (if relevant to restaurant ideas):
- Cuisines: {cuisines}
- Diet type: {diet}
- Allergies: {allergies}

User travel style: {travel_style}

If travel_style suggests:
- "family", "kids", "child" → prefer kid-friendly, low-stress activities.
- "relaxed", "slow", "chilled" → avoid overpacking the plan; leave breaks.
- "adventurous" → include hikes, views, or unique local experiences.
- "romantic" → include scenic spots, cozy cafes, and nice evening walks.

Plan EXACTLY {num_days} days.

For each day, include:
- 🌅 Morning:
- 🌞 Afternoon:
- 🌙 Evening:

Rules:
- Plain text only.
- No HTML, no JSON, no bullet lists.
- Exactly this structure:

Day 1
🌅 Morning: ...
🌞 Afternoon: ...
🌙 Evening: ...

Day 2
...

Keep it realistic and time-conscious.
"""

        return generate(prompt).strip()
