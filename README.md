# ✨ **LifePilot — Your AI-Powered Weekly Planner**

*A Multi-Agent Personal Assistant for Meals, Shopping & Travel*

LifePilot is an intelligent **multi-agent AI assistant** built with **Google GenAI**, **vector memory**, and a polished **Streamlit** interface.
It automates three major weekly tasks for users:

* 🍽 **Weekly Meal Planning**
* 🛒 **Smart Grocery Shopping List Generation**
* ✈ **Travel Itinerary Planning**

Everything runs through one unified query — LifePilot handles routing, memory, and agent orchestration.

---

## 🚀 **Features**

### 🧠 Multi-Agent Architecture

LifePilot uses three specialized agents:

| Agent                | Responsibilities                                          |
| -------------------- | --------------------------------------------------------- |
| **MealPlannerAgent** | Generates weekly meal plans based on preferences & memory |
| **ShoppingAgent**    | Extracts structured shopping lists from meal plans        |
| **TravelAgent**      | Creates clean, emoji-styled itineraries (NO HTML)         |

---

### 🔍 Dynamic Preference Engine

Every user input is analyzed:

* cuisine preferences
* diet (veg / vegan / non-veg)
* disliked ingredients
* allergies
* spice level

Preferences accumulate over time using vector memory.

---

### 🧠 Vector Memory (FAISS)

LifePilot remembers:

* past queries
* food preferences
* prior travel interests
* dietary notes
* implicit behaviour

This helps agents generate more personalized results each time.

---

### 🧰 Google GenAI v1.52.0 (No deprecated configs!)

LifePilot uses:

* `models/gemini-2.0-flash-001` for fast generation
* `models/text-embedding-004` for embeddings

Fully compatible with **google-genai==1.52.0**.

---

### 🖥 Streamlit UI

The UI includes:

* A global input bar
* Selection panel (Meal / Shopping / Travel toggles)
* Tabs for organized output
* Plain-text emoji travel timeline
* Real JSON logs returned from orchestrator
* Fast, clean, responsive interface

---

## 📦 **Project Structure**

```
LifePilot/
│── agents/
│   ├── meal_agent.py
│   ├── shopping_agent.py
│   └── travel_agent.py
│
│── memory/
│   ├── vector_memory.py
│   └── preference_extractor.py
│
│── ui/
│   └── app.py
│
│── gen_client.py
│── orchestrator.py
│── intent.py
│── requirements.txt
│── README.md
│── .gitignore
```

---

## 🔧 **Installation**

### 1. Clone the repo

```bash
git clone https://github.com/yourusername/LifePilot.git
cd LifePilot
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate    # Mac/Linux
venv\Scripts\activate       # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add your API key

Create `.env`:

```
GEN_API_KEY=YOUR_KEY_HERE
```

Or export manually:

```bash
export GEN_API_KEY="your_key"
```

---

## ▶️ **Run LifePilot**

```bash
streamlit run ui/app.py
```

---

## 🧩 **How It Works**

### 1️⃣ User writes any request:

```
Plan my next week. 
Give me vegetarian meals, a shopping list, and a 2-day trip to Dallas.
```

### 2️⃣ Intent detector decides which agents to run:

```
meal: true  
shopping: true  
travel: true
```

### 3️⃣ MealAgent generates a clean weekly plan

### 4️⃣ ShoppingAgent converts meal text → structured JSON

### 5️⃣ TravelAgent returns plain-text grouped itinerary

### 6️⃣ Orchestrator merges everything + logs

---

## 📌 **Travel Itinerary Format (Guaranteed)**

Always plain text:

```
🗓️ Day 1
🌅 Morning
Visit The Dallas World Aquarium.

🌞 Afternoon
Enjoy Klyde Warren Park.

🌙 Evening
Dinner in Deep Ellum.


🗓️ Day 2
🌅 Morning
Perot Museum of Nature & Science.

🌞 Afternoon
Walk Bishop Arts District.

🌙 Evening
Sunset at Reunion Tower.
```

No HTML, no CSS, no Markdown.

---

## 🧪 **Sample Prompts**

```
Give me a vegetarian meal plan for 5 days.
```

```
Create a shopping list for these meals.
```

```
Plan a romantic 2-day trip to Austin.
```

```
I love South Indian food.
```

LifePilot learns continuously.

---

## 📈 **Performance Notes**

* Use `gemini-2.0-flash-001` for best speed
* Agents run in parallel (async) for fast response
* ShoppingAgent includes auto-meal fallback
* Vector memory tracks preferences smartly

---

## 🤝 **Contributing**

Pull requests are welcome!

---

