# ⚡ NexusFlow — Unified Communication Triage System

> AI-powered priority inbox that triage Gmail + Slack messages with LangChain & Gemini

---

## 🏗️ Project Structure

```
nexusflow/
├── backend/
│   ├── main.py              ← FastAPI app (AI triage engine)
│   ├── requirements.txt     ← Python dependencies
│   ├── .env.example         ← API key template
│   └── message_store.json   ← (auto-created) JSON cache
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── index.css
│   │   ├── main.jsx
│   │   └── components/
│   │       ├── Navbar.jsx
│   │       ├── HeroSection.jsx
│   │       ├── StatsGrid.jsx
│   │       ├── FilterBar.jsx
│   │       ├── MessageList.jsx
│   │       ├── MessageCard.jsx
│   │       └── Toast.jsx
│   ├── index.html
│   └── .env
│
├── start.ps1               ← One-click Windows launcher
└── README.md
```

---

## 🚀 Quick Start

### 1. Backend Setup

```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

**Set your API key** (optional — works without it via rule-based fallback):
```powershell
copy .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

**Start the API:**
```powershell
uvicorn main:app --reload --port 8000
```

→ API docs at: http://localhost:8000/docs

---

### 2. Frontend Setup

```powershell
cd frontend
npm install
npm run dev
```

→ Dashboard at: http://localhost:5173

---

## 🤖 AI Triage Logic

| Message Type             | Score | Category                |
|--------------------------|-------|-------------------------|
| Professor / Manager msg  | 7–10  | Urgent/Action Required  |
| Production alerts (P0)   | 9–10  | Urgent/Action Required  |
| Deadline / EOD keywords  | 8–9   | Urgent/Action Required  |
| CI/CD failures, billing  | 5–7   | Informational           |
| Colleague messages       | 4–6   | Informational           |
| Newsletters / Promos     | 1–3   | Ignore/Newsletter       |

**Runs without API key** → uses deterministic rule-based fallback (great for demos!)

---

## 📡 API Endpoints

| Method | Endpoint          | Description                     |
|--------|-------------------|---------------------------------|
| POST   | /api/triage       | Fetch + AI-process all messages |
| GET    | /api/messages     | Get cached messages (filterable)|
| GET    | /api/stats        | Inbox statistics summary        |
| GET    | /api/mock-data    | Preview raw mock messages       |
| DELETE | /api/messages/clear | Clear message store           |

---

## 🔑 Getting a Free Gemini API Key

1. Visit https://aistudio.google.com
2. Sign in with Google → "Get API Key"
3. Copy key → paste in `backend/.env`

---

## 🎯 Demo Script (Hackathon)

1. Open dashboard → http://localhost:5173
2. Click **"Run AI Triage"**
3. Watch messages score and categorize in real-time
4. Show **🔴 Urgent** tab → Professor/Manager messages at top
5. Filter by **Gmail** vs **Slack**
6. Click any card to expand the full message body
7. Point to the **API docs** → http://localhost:8000/docs for technical credibility
