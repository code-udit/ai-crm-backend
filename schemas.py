from pydantic import BaseModel

class InteractionCreate(BaseModel):
    hcp_name: str | None = None
    interaction_type: str | None = None
    date: str | None = None
    time: str | None = None
    attendees: str | None = None
    topics_discussed: str | None = None
    materials_shared: str | None = None
    samples_distributed: str | None = None
    sentiment: str | None = None
    outcomes: str | None = None
    follow_up_actions: str | None = None