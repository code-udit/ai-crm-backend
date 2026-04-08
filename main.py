from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import engine, Base, get_db
import models, schemas
import json
from llm import extract_interaction_data
from agent import app as agent_app
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

@app.get("/health") 
def health():
    return {"status": "ok"}

# Allow frontend (React) to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


allow_credentials=True,
allow_methods=["*"],
allow_headers=["*"],

# Create DB tables automatically
Base.metadata.create_all(bind=engine)


# ------------------ BASIC ROUTES ------------------

@app.get("/")
def home():
    return {"message": "Backend is running"}  # simple check


@app.get("/health")
def health():
    return {"status": "ok"}  # useful for monitoring


# ------------------ CRUD APIs ------------------

@app.post("/interactions")
def create_interaction(data: schemas.InteractionCreate, db: Session = Depends(get_db)):
    # create new DB entry
    new_interaction = models.Interaction(**data.dict())
    db.add(new_interaction)
    db.commit()
    db.refresh(new_interaction)
    return new_interaction


@app.get("/interactions")
def get_interactions(db: Session = Depends(get_db)):
    # return all interactions
    return db.query(models.Interaction).all()


@app.get("/interactions/{id}")
def get_interaction(id: int, db: Session = Depends(get_db)):
    # fetch single interaction
    return db.query(models.Interaction).filter(models.Interaction.id == id).first()


@app.put("/interactions/{id}")
def update_interaction(id: int, data: schemas.InteractionCreate, db: Session = Depends(get_db)):
    interaction = db.query(models.Interaction).filter(models.Interaction.id == id).first()

    if not interaction:
        return {"error": "Interaction not found"}  # basic error handling

    # update each field dynamically
    for key, value in data.dict().items():
        setattr(interaction, key, value)

    db.commit()
    db.refresh(interaction)
    return interaction


# ------------------ AI LOG API ------------------

@app.post("/ai/log")
def ai_log_interaction(message: dict, db: Session = Depends(get_db)):
    
    # 1️⃣ get user message
    user_input = message.get("message")
    if not user_input:
        return {"error": "Message is required"}

    # 2️⃣ call LLM to extract structured data
    llm_output = extract_interaction_data(user_input)
    print("LLM OUTPUT:", llm_output)  # debug log

    # 3️⃣ safely parse JSON
    try:
        data = json.loads(llm_output)
    except:
        return {"error": "Invalid JSON from LLM", "raw": llm_output}

    # 4️⃣ normalize keys to avoid mismatch
    data = {k.lower(): v for k, v in data.items()}

    # 5️⃣ ensure all expected fields exist (avoid frontend crashes)
    fields = [
        "hcp_name", "interaction_type", "date", "time", "attendees",
        "topics_discussed", "materials_shared", "samples_distributed",
        "sentiment", "outcomes", "follow_up_actions"
    ]

    for field in fields:
        data.setdefault(field, None)

    # 6️⃣ save into DB
    new_interaction = models.Interaction(**data)
    db.add(new_interaction)
    db.commit()
    db.refresh(new_interaction)

    return new_interaction


# ------------------ AGENT API ------------------

@app.post("/ai/agent")
def run_agent(message: dict):
    # run LangGraph agent with current form state
    result = agent_app.invoke({
        "input": message.get("message"),
        "data": message.get("data", {})  # existing form data
    })

    # return updated data back to frontend
    return result["data"]  

