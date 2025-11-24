# agents/travel_agent.py

import re
from typing import Any, Dict, List
from gen_client import generate


class TravelAgent:
    """
    Builds a multi-day travel itinerary in plain text.
    """

    def infer_days(self, query: str) -> int:
        q = (query or "").lower()

        m = re.search(r"(\d+)\s*day", q)
        if m:
            try:
                return max(1, int(m.group(1)))
            except ValueError:
                pass

        if "weekend" in q:
            return 2

        if "3 days" in q or "3-day" in q:
            return 3

        # Default if not specified
        return 2

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

User food preferences (if relevant to restaurants):
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
- No HTML, no <div>, no JSON, no bullet lists.
- Exactly this structure:

Day 1
🌅 Morning: ...
🌞 Afternoon: ...
🌙 Evening: ...

Day 2
...

Keep it realistic and family-friendly.
"""

        return generate(prompt).strip()
