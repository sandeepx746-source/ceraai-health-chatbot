from .grok_service import query_grok
from .state_manager import update_context
from deep_translator import GoogleTranslator


def translate_text(text, target_lang):
    if target_lang == "en" or not target_lang:
        return text

    try:
        return GoogleTranslator(source="auto", target=target_lang).translate(text)
    except Exception as e:
        print("Translation Error:", e)
        return text


def generate_response(conversation_id, user_input, language="en"):
    english_input = translate_text(user_input, "en") if language != "en" else user_input

    update_context(conversation_id, "user", english_input, "general", {})

    system_prompt = """
You are CeraAI, a caring health assistant.

Return clean HTML only.
Use only <p>, <strong>, <ul>, <li>, <br>.

Write style:
- Be friendly and caring.
- Explain clearly in simple words.
- Do not write like a textbook.
- Do not give very short answers.
- Do not use same headings every time.
- Give useful explanation + practical tips.
- Answer around 220-320 words.
- Use paragraphs for explanation.
- Use bullets only for important tips.
- End with one caring follow-up question.

For symptoms:
- First explain what the symptom usually means.
- Explain common possible reasons.
- Give what the user can do now.
- Give food/rest/recovery advice if useful.
- Mention danger signs only at the end.
- Do not diagnose.
- Do not prescribe medicines or dosage.

If user writes Tamil/Tanglish, reply in simple Tanglish.
If user writes English, reply in English.
"""

    messages = [{"role": "system", "content": system_prompt}]

    from database.models import ChatHistory

    history_records = (
        ChatHistory.query
        .filter_by(conversation_id=conversation_id)
        .order_by(ChatHistory.timestamp.desc())
        .limit(5)
        .all()
    )

    history_records.reverse()

    if (
        history_records
        and history_records[-1].sender == "user"
        and history_records[-1].message == user_input
    ):
        history_records = history_records[:-1]

    for record in history_records:
        messages.append({
            "role": "user" if record.sender == "user" else "assistant",
            "content": record.message
        })

    messages.append({
        "role": "user",
        "content": english_input
    })

    ai_response = query_grok(messages)

    update_context(conversation_id, "assistant", ai_response)

    return translate_text(ai_response, language) if language != "en" else ai_response