
<div align="center">
  <img src="docs/lifepilot_logo.png" width="120" alt="LifePilot Logo" />

  # ✨ LifePilot — Your Intelligent Planner  
  **A multi-agent AI system that plans Meals, Shopping Lists, and Travel Itineraries intelligently.**

  Designed & Developed with ❤️ by **Saranya Ganesan**  
  <br/><br/>

  ![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
  ![Streamlit](https://img.shields.io/badge/Streamlit-App-red.svg)
  ![Google Gemini](https://img.shields.io/badge/Google%20Gemini-API-00A9FF.svg)
  ![License](https://img.shields.io/badge/License-All%20Rights%20Reserved-orange.svg)
</div>

---

## 🚀 Overview  
**LifePilot** is a smart, multi-agent AI platform that automates:
- 🥗 Meal Planning  
- 🛒 Grocery/Shopping List Generation  
- ✈ Travel Itinerary Planning  

Powered by **Google Gemini**, **vector memory**, and **LLM-based intent detection**, LifePilot learns user preferences over time to deliver personalized plans.

---

## 🌐 Live Deployment  
Your service is deployed on **Google Cloud Run**:

🔗 **Production URL:**  
https://lifepilot-service-254077494572.us-central1.run.app  

---

## 📦 Project Structure
```
LifePilot-Capstone-Project/
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
│── utils/
│   └── validators.py
│
│── gen_client.py
│── orchestrator.py
│── Dockerfile
│── requirements.txt
│── README.md
│── .env.example
│── docs/
│     └── lifepilot_logo.png
```

---
### 📁 **Architecture Diagram**
![Architecture Diagram](docs/architecture.png)

---
## 🔧 Local Setup

### 1️⃣ Create a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate         # Windows
```

### 2️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 3️⃣ Add API Keys  
Create a **.env** file:
```
PRIMARY_GEN_API_KEY="your_key"
BACKUP_GEN_API_KEY=""
THIRD_GEN_API_KEY=""
```

### 4️⃣ Run App Locally
```bash
streamlit run ui/app.py
```

---

## 🐳 Docker Deployment

### Build Image
```bash
docker build -t lifepilot .
```

### Run Container
```bash
docker run -p 8080:8080 -e PRIMARY_GEN_API_KEY="your_key" lifepilot
```

---

## ☁ Deploy to Google Cloud Run

### Enable APIs
```bash
gcloud services enable run.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com secretmanager.googleapis.com
```

### Build & Push Image
```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/lifepilot .
```

### Deploy
```bash
gcloud run deploy lifepilot    --image gcr.io/PROJECT_ID/lifepilot    --platform managed    --region us-central1    --set-env-vars PRIMARY_GEN_API_KEY=projects/PROJECT_ID/secrets/GEN_API_KEY/versions/latest    --allow-unauthenticated
```

---

## 🧪 Testing the Application  
Examples included in **TEST_CASES.md**.

---

## 📜 License  
© 2025 Saranya. All Rights Reserved.  
No redistribution or commercial reuse without permission.

