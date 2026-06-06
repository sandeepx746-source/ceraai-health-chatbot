# A simple dictionary-based session state manager for context
# In a production environment with multiple servers, use Redis or DB

conversation_sessions = {}

def get_context(conversation_id):
    if conversation_id not in conversation_sessions:
        conversation_sessions[conversation_id] = {
            'history': [],
            'current_intent': None,
            'entities': {}
        }
    return conversation_sessions[conversation_id]

def update_context(conversation_id, role, content, intent=None, entities=None):
    context = get_context(conversation_id)
    context['history'].append({"role": role, "content": content})
    
    # Keep only last 10 messages for context window
    if len(context['history']) > 10:
        context['history'] = context['history'][-10:]
        
    if intent:
        context['current_intent'] = intent
    if entities:
        context['entities'].update(entities)

def clear_context(conversation_id):
    if conversation_id in conversation_sessions:
        conversation_sessions[conversation_id] = {
            'history': [],
            'current_intent': None,
            'entities': {}
        }
