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
        Robustly infer number of days from natural language.
        """
        if not query:
            return 1

        q = query.lower().strip()

        # 1. Numeric patterns: "2 days", "3-day trip"
        m = re.search(r"(\d+)\s*[- ]?\s*day", q)
        if m:
            try:
                n = int(m.group(1))
                if n >= 1:
                    return min(n, 10)
            except Exception:
                pass

        # 2. Spelled-out numbers
        for word, num in self.NUMBER_WORDS.items():
            if re.search(rf"{word}\s*[- ]?\s*day", q):
                return num
            if re.search(rf"{word}\s+days", q):
                return num

        # 3. Weekend
        if "weekend" in q:
            return 2

        # 4. Overnight / short trip
        if "overnight" in q:
            return 1

        one_day_triggers = ["quick trip", "short trip", "day trip", "tomorrow"]
        if any(w in q for w in one_day_triggers):
            return 1

        # 5. Generic trip mention → default 2
        if any(w in q for w in ["trip", "travel", "visit", "vacation"]):
            return 2

        # 6. Fallback
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

User food preferences (for suggesting vegetarian-friendly places only):
- Cuisines: {cuisines}
- Diet type: {diet}
- Allergies: {allergies}

User travel style (if any): {travel_style}

Plan EXACTLY {num_days} days.

For each day, include:
- 🌅 Morning:
- 🌞 Afternoon:
- 🌙 Evening:

Rules:
- Plain text only.
- No HTML, no JSON, no bullet lists.
- Follow exactly this structure:

Day 1
🌅 Morning: ...
🌞 Afternoon: ...
🌙 Evening: ...

Day 2
...

Keep it realistic and family-friendly.
Mention vegetarian / vegan-friendly restaurants only when relevant,
but do not output a separate meal plan.
"""

        return generate(prompt).strip()
