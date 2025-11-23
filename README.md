✅ README.md (FINAL VERSION FOR YOUR PROJECT)
# ✨ LifePilot — AI Powered Weekly Planner  
Plan Meals • Shopping Lists • Travel Itineraries • Personalized with Memory

LifePilot is an AI-powered assistant that plans your meals, shopping lists, and travel itineraries — all personalized using long-term user memory.

It uses:
- Google Gemini AI (via `google-genai`)
- Multi-agent architecture (Meal, Shopping, Travel)
- Vector memory with automatic preference extraction
- Streamlit UI with tabs, downloadable PDFs, and preference viewer
- Docker-ready deployment

---

## 🚀 Features

### 🔥 Intelligent Multi-Agent System
LifePilot includes 3 specialized agents:
- **Meal Planner Agent** — Creates meal plans based on memory + dietary preferences.
- **Shopping Agent** — Generates a smart grocery list from meal plans.
- **Travel Agent** — Builds itineraries grouped visually by *Morning / Afternoon / Evening*.

### 🧠 Persistent Memory
LifePilot remembers:
- Food preferences (veg, vegan, non-veg)
- Cuisines (South Indian, Italian, etc.)
- Allergies & dislikes
- Spice level
- Implicit user patterns

Preferences improve future outputs automatically.

### 🖥️ Streamlit UI
- Tabs for **Meal Plan**, **Shopping List**, **Travel Itinerary**
- **Raw JSON Logs** tab for debugging agent behavior
- **Preferences Viewer**
- **Download as PDF** button for each tab

### 🧪 Built-in Test Cases
Ready-to-run test scenarios to validate:
- Memory retention  
- Multi-agent orchestration  
- Intent detection  
- Combined requests  

### 🐳 Docker Support
Run LifePilot anywhere with a single command.

---

# 📦 Project Structure



LifePilot/
│
├── ui/
│ └── app.py # Streamlit UI
│
├── agents/
│ ├── meal_agent.py
│ ├── shopping_agent.py
│ └── travel_agent.py
│
├── memory/
│ ├── vector_memory.py
│ ├── preference_extractor.py
│ └── init.py
│
├── orchestrator.py # Central controller
├── gen_client.py # Gemini API wrapper
├── requirements.txt
├── Dockerfile
└── README.md


---

# 🔑 Environment Setup

### 1️⃣ Clone the repo
```bash
git clone https://github.com/<yourname>/LifePilot.git
cd LifePilot

2️⃣ Install dependencies
pip install -r requirements.txt

3️⃣ Create environment variable for Gemini

Create .env:

GOOGLE_API_KEY=your_key_here


Or export directly:

export GOOGLE_API_KEY="your_key_here"

▶️ Running the App
streamlit run ui/app.py


Open in browser:

http://localhost:8501

🧪 Test Cases for Validating the Entire Project

These test cases help anyone confirm:

Memory works

Intent detection works

Agents run correctly

Combined requests work

Edge cases behave as expected

✅ Test Case 1 — Memory Retention

Step 1

I love South Indian vegetarian food.


Expected:
No agents run. Preferences updated.

Step 2

Give me a 3-day meal plan.


Expected:
Meal plan is South Indian + vegetarian, based on stored memory.

✅ Test Case 2 — Travel Only with Memory Context

Step 1

I prefer mild spice and I’m vegetarian.


Step 2

Plan a 2-day trip to Delhi.


Expected:

Only TravelAgent runs

Output does NOT include meals

Preferences should not affect travel itinerary