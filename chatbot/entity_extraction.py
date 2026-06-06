import json
from .grok_service import query_grok

def extract_entities(user_input):
    """
    Extract entities such as disease_name, symptoms, location, age, vaccine_name
    Returns a dictionary of entities.
    """
    messages = [
        {"role": "system", "content": "You are an Entity Extraction module. Extract entities from the user's health query. Possible entities: [disease_name, symptoms, location, age, vaccine_name]. Return a JSON object with these keys if they exist in the text. Do not output any other text."},
        {"role": "user", "content": f"User Input: {user_input}"}
    ]
    
    try:
        response = query_grok(messages)
        if response.startswith("```json"):
            response = response[7:-3]
        elif response.startswith("```"):
            response = response[3:-3]
        data = json.loads(response.strip())
        return data
    except Exception as e:
        print(f"Entity Extraction Error: {e}")
        return {}
