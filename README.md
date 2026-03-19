<div align="center">
  <img src="docs/lifepilot_logo.png" width="120" alt="LifePilot Logo" />

  # LifePilot - Your Intelligent Planner
  **A multi-agent AI system that plans meals, shopping lists, and travel itineraries intelligently.**

  Designed and developed by **Saranya Ganesan**
  <br/><br/>

  ![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
  ![Streamlit](https://img.shields.io/badge/Streamlit-App-red.svg)
  ![Google Gemini](https://img.shields.io/badge/Google%20Gemini-API-00A9FF.svg)
  ![License](https://img.shields.io/badge/License-All%20Rights%20Reserved-orange.svg)
</div>

---

## Overview
**LifePilot** is a smart multi-agent AI platform that automates:
- Meal planning
- Grocery and shopping list generation
- Travel itinerary planning

Powered by **Google Gemini**, **vector memory**, and **intent detection**, LifePilot learns user preferences over time to deliver more personalized plans.

---

## Live Deployment
Production URL:

https://lifepilot-service-254077494572.us-central1.run.app

---

## Project Structure
```text
LifePilot-Capstone-Project/
|-- agents/
|   |-- meal_agent.py
|   |-- shopping_agent.py
|   `-- travel_agent.py
|
|-- memory/
|   |-- preference_extractor.py
|   `-- vector_memory.py
|
|-- ui/
|   `-- app.py
|
|-- utils/
|   `-- validators.py
|
|-- gen_client.py
|-- orchestrator.py
|-- test_gemini.py
|-- Dockerfile
|-- requirements.txt
|-- README.md
`-- docs/
    `-- lifepilot_logo.png
```

### Architecture Diagram
![Architecture Diagram](docs/architecture%20diagram.png)

---

## Local Setup

### 1. Prerequisites
- Python 3.10 or newer
- `pip`
- A Google Gemini API key

### 2. Clone the project
```bash
git clone https://github.com/saranyaganesandeveloper/LifePilot-Capstone-Project.git
cd LifePilot-Capstone-Project
```

### 3. Create a virtual environment
```bash
python -m venv venv
```

Windows PowerShell:
```powershell
.\venv\Scripts\Activate.ps1
```

macOS / Linux:
```bash
source venv/bin/activate
```

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

### 5. Create the `.env` file
Create a `.env` file in the project root with:

```env
PRIMARY_GEN_API_KEY="your_key"
BACKUP_GEN_API_KEY=""
THIRD_GEN_API_KEY=""
GEMINI_MODEL="models/gemini-flash-latest"
```

Notes:
- `PRIMARY_GEN_API_KEY` is required.
- `GEMINI_MODEL` is optional, but this default follows the latest Gemini Flash alias.
- Keep `.env` local only and do not commit real API keys.

### 6. Verify Gemini is working
Run the smoke test from the project root:

```bash
python test_gemini.py
```

Expected result:
- It prints the configured model.
- It returns a short Gemini response.
- It ends with `Smoke test completed.`

### 7. Run the Streamlit app
Start the app from the project root:

```bash
streamlit run ui/app.py
```

If `streamlit` is not recognized, use:

```bash
python -m streamlit run ui/app.py
```

Then open the local URL shown in the terminal, usually:

```text
http://localhost:8501
```

### 8. Troubleshooting
- If the smoke test fails, verify your API key in `.env`.
- If you update `.env`, restart Streamlit so the new values are loaded.
- If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process Bypass`.
- If you get missing-module errors, make sure the virtual environment is activated before running the app.

---

## Docker Deployment

### Build Image
```bash
docker build -t lifepilot .
```

### Run Container
```bash
docker run -p 8080:8080 -e PRIMARY_GEN_API_KEY="your_key" lifepilot
```

---

## Deploy to Google Cloud Run

### Enable APIs
```bash
gcloud services enable run.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com secretmanager.googleapis.com
```

### Build and Push Image
```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/lifepilot .
```

### Deploy
```bash
gcloud run deploy lifepilot \
  --image gcr.io/PROJECT_ID/lifepilot \
  --platform managed \
  --region us-central1 \
  --set-env-vars PRIMARY_GEN_API_KEY=projects/PROJECT_ID/secrets/GEN_API_KEY/versions/latest \
  --allow-unauthenticated
```

---

## Testing
Examples are included in `test_cases.md`.

---

## License
Copyright 2025 Saranya Ganesan. All rights reserved.
No redistribution or commercial reuse without permission.
