import json
from .grok_service import query_grok

def detect_intent(user_input):
    """
    Use Grok API to detect intent.
    Intents: symptom_check, vaccination_info, disease_awareness, prevention_tips, emergency_help, general_greeting
    """
    messages = [
        {"role": "system", "content": "You are an Intent Detection module for a Public Health Chatbot. Output only a JSON object with a single key 'intent' whose value is one of: [symptom_check, vaccination_info, disease_awareness, prevention_tips, emergency_help, general_greeting, unknown]. Do not output any other text."},
        {"role": "user", "content": f"User Input: {user_input}"}
    ]
    
    try:
        response = query_grok(messages)
        # Clean response in case of markdown
        if response.startswith("```json"):
            response = response[7:-3]
        data = json.loads(response.strip())
        return data.get('intent', 'unknown')
    except Exception as e:
        print(f"Intent Detection Error: {e}")
        return "unknown"
