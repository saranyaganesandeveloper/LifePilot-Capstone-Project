# agents/travel_agent.py

from gen_client import generate
import re


class TravelAgent:

    def run(self, user_query: str, memory_context: list, prefs: dict):
        prompt = f"""
You are a travel itinerary planner.

Return a 2-day itinerary in PLAIN TEXT grouped format with emojis.

STRICT RULES:
- NO HTML
- NO CSS
- NO <div>, <span>, <br>, style attributes
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

Memory context:
{memory_context}

Return ONLY plain text grouped with emojis in this format. Nothing else.
"""
        try:
            raw = generate(prompt)

            # Remove any stray HTML if the model tries to be fancy
            cleaned = re.sub(r"<[^>]+>", "", raw)
            cleaned = re.sub(r"<!--.*?-->", "", cleaned, flags=re.DOTALL)

            # Remove markdown artifacts
            cleaned = re.sub(r"[#*_`>-]", "", cleaned)

            # Normalize excessive blank lines
            cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)

            return cleaned.strip()

        except Exception as e:
            return f"[TravelAgent Error] {str(e)}"
