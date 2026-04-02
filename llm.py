from groq import Groq
import re

client = Groq(api_key="GROQ_API_KEY")

def call_llm(prompt: str):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

def extract_interaction_data(user_input: str):
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")

    prompt = f"""
    Extract structured data from the text and return ONLY valid JSON.

    Today's date: {today}

    Rules:
    - sentiment must be one of: Positive, Neutral, Negative
    - interaction_type must be one of: Meeting, Call, Email, Other
    - convert relative dates like "yesterday", "today" using today's date
    - ALL fields must be STRING or null (NO lists)
    - follow_up_actions must be a complete sentence
    - outcomes must be inferred if possible (e.g., "Doctor showed interest")

    Fields:
    - hcp_name
    - interaction_type
    - date
    - time
    - attendees
    - topics_discussed
    - materials_shared
    - samples_distributed
    - sentiment
    - outcomes
    - follow_up_actions

    Text:
    {user_input}
    """

    response = call_llm(prompt)
    return clean_json_output(response)

def clean_json_output(text: str):
    match = re.search(r'\{.*\}', text, re.DOTALL)
    return match.group(0) if match else text