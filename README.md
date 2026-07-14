# ✈️ TravelPlannerPro

> **AI-Powered Travel Planner Agent** — IBM SkillsBuild Final Project  
> Problem Statement No. 5 — Travel Planner Agent | Edunet Foundation

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0-black?logo=flask)
![IBM watsonx](https://img.shields.io/badge/IBM-watsonx.ai-0062ff?logo=ibm)
![IBM Granite](https://img.shields.io/badge/IBM-Granite_Model-0062ff?logo=ibm)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple?logo=bootstrap)

---

## 🌍 Project Overview

**TravelPlannerPro** is a professional, production-ready AI-powered travel planner web application built with **Python Flask** and **IBM watsonx.ai**. The AI agent — named **ARIA (AI Roaming Itinerary Assistant)** — uses IBM Granite foundation models to generate highly personalized, day-wise travel itineraries complete with budget analysis, hotel recommendations, food guides, hidden gems, safety guidelines, and more.

This project was developed for **Problem Statement No. 5 — Travel Planner Agent** as part of the **Edunet Foundation IBM SkillsBuild** internship program.

---

## ✨ Features

### 🤖 AI-Powered Itinerary Generation
- Personalized day-wise travel plans via **IBM Granite** (`ibm/granite-13b-instruct-v2`)
- 18+ report sections covering every aspect of travel planning
- Budget optimization across budget, mid-range, and luxury tiers
- Hidden gems and off-beat destination recommendations

### 💬 Interactive AI Chat Assistant (ARIA)
- Real-time conversational travel assistant
- Maintains chat history across the session
- Context-aware responses using your trip details
- Quick prompt chips for instant answers

### 📊 Comprehensive Travel Report
| Section | Description |
|---------|-------------|
| 📋 Executive Summary | High-level trip overview |
| 📅 Day-wise Itinerary | Hour-by-hour schedule |
| 💰 Budget Breakdown | Itemised cost table |
| 🏨 Accommodation | Budget to luxury options |
| 🚌 Transportation | Routes and booking tips |
| 🍽️ Food Guide | Local cuisine & restaurants |
| 🧭 Hidden Gems | Off-beat local favourites |
| 🌦️ Weather Overview | Seasonal guide & packing |
| 🎒 Packing Checklist | Categorised essentials |
| 🛡️ Safety Guidelines | Emergency contacts & tips |
| 🌍 Culture & Etiquette | Local customs guide |
| 💡 Money-Saving Tips | Smart budget hacks |
| ⭐ Travel Readiness Score | Visual readiness gauge |

### 📄 Professional PDF Export
- ReportLab-powered PDF with cover page
- Trip summary table, full itinerary, budget tables
- IBM Granite branding and metadata

### 🎨 Premium UI/UX
- Dark/Light mode toggle with localStorage persistence
- Animated hero section with floating particles
- Split-pane workspace (itinerary + chat)
- Fully responsive Bootstrap 5 layout
- Mobile-first design

---

## 🧰 Technology Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.11+, Flask 3.0 |
| **AI Model** | IBM Granite (`ibm/granite-13b-instruct-v2`) |
| **AI Platform** | IBM watsonx.ai |
| **AI SDK** | `ibm-watsonx-ai` |
| **Frontend** | Bootstrap 5.3, Vanilla JS |
| **PDF Export** | ReportLab |
| **Deployment** | Render / Gunicorn |
| **Config** | python-dotenv |

---

## 🤖 IBM Granite Integration

TravelPlannerPro integrates IBM Granite through the official **ibm-watsonx-ai SDK**:

```python
from ibm_watsonx_ai import APIClient, Credentials
from ibm_watsonx_ai.foundation_models import ModelInference

credentials = Credentials(url=IBM_ENDPOINT_URL, api_key=IBM_API_KEY)
client = APIClient(credentials=credentials)
model = ModelInference(
    model_id="ibm/granite-13b-instruct-v2",
    api_client=client,
    project_id=IBM_PROJECT_ID,
    params={
        GenParams.MAX_NEW_TOKENS: 2048,
        GenParams.TEMPERATURE: 0.7,
        GenParams.TOP_P: 0.95,
    }
)
```

**AGENT_INSTRUCTIONS** in `config.py` configures the AI persona, travel styles (solo, family, luxury, adventure, sustainable, Indian tourism), behavior guidelines, and responsible AI principles.

---

## 📦 Installation

### Prerequisites
- Python 3.11+
- IBM Cloud account (free Lite tier works)
- IBM watsonx.ai project

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/TravelPlannerPro.git
cd TravelPlannerPro
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate      # macOS/Linux
venv\Scripts\activate         # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
cp .env.example .env
# Edit .env with your IBM credentials
```

---

## 🔐 Environment Variables

Create a `.env` file in the project root with:

```env
# IBM watsonx.ai — get from https://cloud.ibm.com
IBM_API_KEY=your_ibm_cloud_api_key
IBM_PROJECT_ID=your_watsonx_project_id
IBM_ENDPOINT_URL=https://us-south.ml.cloud.ibm.com
IBM_MODEL_ID=ibm/granite-13b-instruct-v2

# Flask
SECRET_KEY=your-secret-key
FLASK_ENV=development
PORT=5000
```

### How to get IBM credentials:
1. Log in to [IBM Cloud](https://cloud.ibm.com) (free Lite account works)
2. Create an **IBM watsonx.ai** service instance
3. Create a **Project** in watsonx.ai studio
4. Generate an **API Key** from IAM → API Keys
5. Copy your **Project ID** from the project settings

> **Demo Mode:** If IBM credentials are not set, the app runs automatically in **Demo Mode** with pre-configured sample responses — no setup required.

---

## 🚀 Running Locally

```bash
# Development server
python run.py

# OR with Flask CLI
flask --app run run --debug

# OR with Gunicorn (production-like)
gunicorn run:app --bind 0.0.0.0:5000 --workers 2
```

Open http://localhost:5000 in your browser.

---

## ☁️ Render Deployment

### Automatic Deployment (render.yaml)

The project includes a `render.yaml` for one-click deployment:

1. Push code to GitHub
2. Go to [render.com](https://render.com) → New → Web Service
3. Connect your GitHub repo
4. Render auto-detects `render.yaml`
5. Add **Environment Variables** in the Render dashboard:
   - `IBM_API_KEY`
   - `IBM_PROJECT_ID`
6. Deploy!

### Manual Render Setup

| Setting | Value |
|---------|-------|
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn run:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120` |
| **Python Version** | `3.11.0` |

---

## 📁 Project Structure

```
TravelPlannerPro/
├── run.py                          # Application entry point
├── config.py                       # Configuration + AGENT_INSTRUCTIONS
├── requirements.txt                # Python dependencies
├── Procfile                        # Gunicorn process file
├── render.yaml                     # Render deployment config
├── .env.example                    # Environment variable template
├── README.md                       # This file
│
├── app/
│   ├── __init__.py                 # Flask application factory
│   ├── routes/
│   │   ├── main_routes.py          # Page routes (/, /dashboard, /workspace)
│   │   └── api_routes.py           # REST API (/api/*)
│   ├── services/
│   │   ├── watsonx_service.py      # IBM watsonx.ai / Granite integration
│   │   └── travel_service.py       # Travel plan generation & chat logic
│   └── utils/
│       ├── pdf_generator.py        # ReportLab PDF report generator
│       └── validators.py           # Input validation & sanitization
│
├── templates/
│   ├── index.html                  # Landing page (hero + features)
│   ├── dashboard.html              # Trip planning form
│   └── workspace.html              # Itinerary viewer + ARIA chat
│
└── static/
    ├── css/style.css               # Custom stylesheet (dark/light mode)
    ├── js/main.js                  # Frontend JS (form, chat, PDF, markdown)
    └── exports/                    # Generated PDFs (auto-created)
```

---

## 🌐 API Reference

All endpoints return JSON: `{"success": true, "data": {...}}` or `{"success": false, "error": "..."}`.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Health check |
| `GET` | `/api/status` | App & IBM integration status |
| `POST` | `/api/generate-itinerary` | Generate AI travel plan |
| `POST` | `/api/chat` | Chat with ARIA |
| `POST` | `/api/chat/clear` | Clear chat history |
| `POST` | `/api/export-pdf` | Export travel report as PDF |

### Example: Generate Itinerary

```bash
curl -X POST http://localhost:5000/api/generate-itinerary \
  -H "Content-Type: application/json" \
  -d '{
    "source": "Mumbai",
    "destination": "Goa",
    "departure_date": "2025-12-20",
    "return_date": "2025-12-27",
    "travelers": 2,
    "budget": "Mid-Range (₹50,000–₹1,00,000)",
    "travel_style": "couple",
    "transport": "flight",
    "hotel_pref": "boutique",
    "interests": "beaches, food, nightlife"
  }'
```

---

## 🎯 Travel Styles Supported

| Style | Focus |
|-------|-------|
| 🧳 Solo | Safety, flexibility, budget-friendly |
| 👨‍👩‍👧 Family | Kid-friendly, convenient, safe |
| 💼 Business | Connectivity, efficiency, comfort |
| 🏔️ Adventure | Trekking, outdoor, extreme sports |
| 👑 Luxury | 5-star, exclusive, VIP experiences |
| 🌿 Sustainable | Eco-friendly, responsible tourism |
| 🪷 Indian Tourism | Heritage, culture, Incredible India |
| 💑 Couple | Romantic getaways, honeymoon plans |

---

## 🤝 Responsible AI

TravelPlannerPro follows IBM's responsible AI principles:
- **Transparency**: AI-generated content is clearly labelled
- **Accuracy**: Users are encouraged to verify visa/health info from official sources
- **Inclusivity**: Accessible options across all budget ranges
- **Privacy**: No sensitive personal/financial data is stored
- **Bias Mitigation**: Balanced recommendations across all travel styles

---

## 📜 License

MIT License — feel free to use, modify, and distribute.

---

## 🙏 Acknowledgements

- **IBM watsonx.ai** — AI platform and Granite foundation models
- **Edunet Foundation** — IBM SkillsBuild internship program
- **Flask** — Lightweight Python web framework
- **Bootstrap** — Responsive UI framework
- **ReportLab** — PDF generation library

---

<div align="center">
  <strong>Built with ❤️ using IBM Granite · IBM watsonx.ai · Flask</strong><br/>
  <em>Edunet Foundation IBM SkillsBuild | Problem Statement No. 5 — Travel Planner Agent</em>
</div>
# Travelplanner-AI
