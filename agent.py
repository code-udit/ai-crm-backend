from langgraph.graph import StateGraph, END
from typing import TypedDict, Dict, Any
from llm import extract_interaction_data
import json
from database import SessionLocal
import models


# ------------------ STATE ------------------

# simple shared state across tools
class State(TypedDict, total=False):
    input: str
    data: Dict[str, Any]


graph = StateGraph(State)


# ------------------ TOOLS ------------------

def log_interaction_tool(state: State):
    # first-time extraction from user input
    user_input = state.get("input")

    llm_output = extract_interaction_data(user_input)

    try:
        data = json.loads(llm_output)
    except:
        # fallback if LLM returns bad JSON
        data = {"error": "Invalid JSON", "raw": llm_output}

    return {"data": data}


def edit_interaction_tool(state: State):
    # update only specific fields
    user_input = state.get("input")
    existing_data = state.get("data", {})

    prompt = f"""
    You are updating an existing JSON.

    Existing Data:
    {existing_data}

    Instruction:
    {user_input}

    RULES:
    - Only update fields mentioned in instruction
    - KEEP all other fields unchanged
    - Return FULL JSON (not partial)

    Output ONLY JSON.
    """

    llm_output = extract_interaction_data(prompt)

    try:
        updated_data = json.loads(llm_output)
    except:
        updated_data = {}

    # merge safely → avoid wiping old data
    final_data = existing_data.copy()
    final_data.update(updated_data)

    return {"data": final_data}


# ------------------ ROUTER ------------------

def router(state: State):
    # decides which tool to call
    user_input = state.get("input", "").lower()

    if "id" in user_input:
        return {"next": "fetch_tool"}

    elif "follow" in user_input or "suggest" in user_input:
        return {"next": "followup_tool"}

    elif "change" in user_input or "update" in user_input:
        return {"next": "edit_tool"}

    elif any(word in user_input for word in ["happy", "sad", "good", "bad", "angry", "positive", "negative"]):
        return {"next": "sentiment_tool"}

    else:
        return {"next": "log_tool"}


# ------------------ FETCH TOOL ------------------

def fetch_interaction_tool(state: State):
    user_input = state.get("input", "")

    # simple ID extraction
    words = user_input.split()
    interaction_id = None

    for w in words:
        if w.isdigit():
            interaction_id = int(w)
            break

    if not interaction_id:
        return {"data": None}

    db = SessionLocal()
    interaction = db.query(models.Interaction).filter(models.Interaction.id == interaction_id).first()
    db.close()

    if not interaction:
        return {"data": None}

    # convert SQLAlchemy object → dict
    data = interaction.__dict__
    data.pop("_sa_instance_state", None)

    return {"data": data}


# ------------------ SENTIMENT TOOL ------------------

def sentiment_tool(state: State):
    user_input = state.get("input", "")
    existing_data = state.get("data", {})

    from llm import call_llm

    prompt = f"""
    Analyze the sentiment of the text.

    Return ONLY one word:
    Positive or Neutral or Negative

    Text:
    {user_input}
    """

    llm_output = call_llm(prompt)
    sentiment = llm_output.strip().replace('"', '')

    # update only sentiment (keep rest)
    final_data = existing_data.copy()
    final_data["sentiment"] = sentiment

    return {"data": final_data}


# ------------------ FOLLOW-UP TOOL ------------------

def followup_tool(state: State):
    existing_data = state.get("data", {})

    from llm import call_llm

    prompt = f"""
    Based on this interaction data, suggest 2-3 follow-up actions.

    Data:
    {existing_data}

    Return as short bullet points (1 line each).
    """

    llm_output = call_llm(prompt)

    # add suggestions without removing existing data
    final_data = existing_data.copy()
    final_data["follow_up_suggestions"] = llm_output

    return {"data": final_data}


# ------------------ GRAPH SETUP ------------------

graph.add_node("router", router)
graph.add_node("log_tool", log_interaction_tool)
graph.add_node("edit_tool", edit_interaction_tool)
graph.add_node("fetch_tool", fetch_interaction_tool)
graph.add_node("followup_tool", followup_tool)
graph.add_node("sentiment_tool", sentiment_tool)

graph.set_entry_point("router")

# routing logic
graph.add_conditional_edges(
    "router",
    lambda x: x["next"],
    {
        "log_tool": "log_tool",
        "edit_tool": "edit_tool",
        "fetch_tool": "fetch_tool",
        "sentiment_tool": "sentiment_tool",
        "followup_tool": "followup_tool"
    }
)

# simple flow endings
graph.add_edge("log_tool", END)
graph.add_edge("edit_tool", END)
graph.add_edge("followup_tool", END)
graph.add_edge("sentiment_tool", END)

# fetch → edit (so user can update fetched data)
graph.add_edge("fetch_tool", "edit_tool")

# compile graph
app = graph.compile()


# ------------------ TEST ------------------

if __name__ == "__main__":
    result = app.invoke({
        "input": "Suggest follow up actions",
        "data": {
            "hcp_name": "Dr Sharma",
            "topics_discussed": "diabetes drug",
            "sentiment": "Positive"
        }
    })

    print(result)
    print(result["data"])