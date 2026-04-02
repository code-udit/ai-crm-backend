🚀 AI CRM Backend (LangGraph + FastAPI)

📌 Overview

This is an AI-powered CRM backend that converts natural language interactions into structured data using LangGraph + LLMs.
It supports logging, editing, fetching, sentiment analysis, and follow-up suggestions for healthcare interactions.

---

🧠 Features

- ✅ Natural language → structured interaction data
- ✅ LangGraph-based multi-tool agent
- ✅ CRUD APIs with FastAPI
- ✅ PostgreSQL database integration
- ✅ AI-powered:
  - Interaction logging
  - Data editing
  - Sentiment analysis
  - Follow-up suggestions

---

🛠️ Tech Stack

- Backend: FastAPI
- AI Orchestration: LangGraph
- LLM: (Gemma / configured model)
- Database: PostgreSQL (SQLAlchemy ORM)
- Language: Python

---

⚙️ Setup Instructions

1️⃣ Clone repository

git clone <your-repo-link>
cd ai-crm-backend

2️⃣ Create virtual environment

python -m venv venv
venv\Scripts\activate   # Windows

3️⃣ Install dependencies

pip install -r requirements.txt

4️⃣ Setup environment variables

Create ".env" file:

DATABASE_URL=postgresql://user:password@localhost:5432/dbname
API_KEY=your_llm_api_key

---

5️⃣ Run backend

uvicorn main:app --reload

👉 Server runs at:

http://127.0.0.1:8000

---

📡 API Endpoints

🔹 Health Check

GET /health

🔹 Create Interaction

POST /interactions

🔹 Get All Interactions

GET /interactions

🔹 Get Interaction by ID

GET /interactions/{id}

🔹 Update Interaction

PUT /interactions/{id}

🔹 AI Log Interaction

POST /ai/log

🔹 AI Agent (LangGraph)

POST /ai/agent

---

🤖 LangGraph Tools

1. Log Interaction Tool

Extracts structured data from user input.

2. Edit Interaction Tool

Updates existing interaction fields.

3. Fetch Interaction Tool

Retrieves interaction from database using ID.

4. Sentiment Tool

Analyzes sentiment from text.

5. Follow-up Tool

Generates follow-up suggestions.

---

🔄 Workflow

1. User sends natural language input
2. Router selects appropriate tool
3. Tool processes data
4. Returns structured JSON
5. Data stored or updated in DB

---

🧪 Example

🔹 Input

Met Dr Sharma yesterday, discussed diabetes drug, he was interested

🔹 Output

{
  "hcp_name": "Dr Sharma",
  "interaction_type": "Meeting",
  "date": "2026-03-30",
  "time": null,
  "attendees": null,
  "topics_discussed": "diabetes drug",
  "materials_shared": null,
  "samples_distributed": null,
  "sentiment": "Positive",
  "outcomes": "Doctor showed interest",
  "follow_up_actions": "Schedule follow-up discussion next week"
}

---

📌 Notes

- Ensure PostgreSQL is running
- Use correct API key for LLM
- LangGraph manages tool orchestration

---

⭐ Future Improvements

- Add authentication (JWT)
- Improve LLM schema validation
- Add logging & monitoring
- Deploy using Docker + Cloud

---