# agents/travel_agent.py

from gen_client import generate
import re


class TravelAgent:
    """
    Generates a 2-day travel itinerary as plain text grouped by day and time of day,
    with emojis, and strictly no HTML or markdown formatting.
    """

    def run(self, user_query: str, memory_context: list, prefs: dict) -> str:
        prompt = f"""
You are a travel itinerary planner.

Return a 2-day itinerary in PLAIN TEXT grouped format with emojis.

STRICT RULES:
- NO HTML
- NO CSS
- NO <div>, <span>, <br>, or style attributes
- NO markdown formatting (#, **, *, ``` )
- MUST use emojis:
    🗓️ for each Day
    🌅 for Morning
    🌞 for Afternoon
    🌙 for Evening

FORMAT EXACTLY LIKE:

🗓️ Day 1
🌅 Morning
<plan>

🌞 Afternoon
<plan>

🌙 Evening
<plan>


🗓️ Day 2
🌅 Morning
<plan>

🌞 Afternoon
<plan>

🌙 Evening
<plan>

User request:
{user_query}

User preferences (JSON-like):
{prefs}

Relevant memory context:
{memory_context}

Return ONLY plain text grouped with emojis in this format. Nothing else.
"""
        try:
            raw = generate(prompt)

            # Remove any stray HTML if model misbehaves
            cleaned = re.sub(r"<[^>]+>", "", raw)
            cleaned = re.sub(r"<!--.*?-->", "", cleaned, flags=re.DOTALL)

            # Remove markdown artifacts
            cleaned = re.sub(r"[#*_`>-]", "", cleaned)

            # Normalize extra blank lines
            cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)

            return cleaned.strip()

        except Exception as e:
            return f"[TravelAgent Error] {str(e)}"
