def check_slots(intent, entities):
    """
    Check if required slots for an intent are filled.
    Returns (True, None) if all slots filled, (False, missing_slot_name) if not.
    """
    required_slots = {
        'symptom_check': ['symptoms'],
        'vaccination_info': ['vaccine_name', 'age'],
        # Other intents might not strictly require slots to generate a general response
    }
    
    if intent in required_slots:
        for slot in required_slots[intent]:
            if slot not in entities or not entities[slot]:
                return False, slot
                
    return True, None
