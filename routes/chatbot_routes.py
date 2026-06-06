from flask import Blueprint, request, jsonify
from flask_login import current_user, login_required
from database.db import db
from database.models import ChatHistory, Conversation
from chatbot.response_generator import generate_response

chatbot_bp = Blueprint('chatbot', __name__)


@chatbot_bp.route('/api/chat', methods=['POST'])
@login_required
def chat():
    data = request.get_json() or {}

    user_message = data.get('message', '').strip()
    conversation_id = data.get('conversation_id')
    language = current_user.language_pref

    if not user_message:
        return jsonify({'error': 'No message provided'}), 400

    if not conversation_id:
        title = (user_message[:30] + '...') if len(user_message) > 30 else user_message

        new_conv = Conversation(
            title=title,
            user_id=current_user.id
        )

        db.session.add(new_conv)
        db.session.commit()

        conversation_id = new_conv.id

    else:
        conv = Conversation.query.get(conversation_id)

        if not conv or conv.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403

    user_chat = ChatHistory(
        message=user_message,
        sender='user',
        conversation_id=conversation_id
    )

    db.session.add(user_chat)
    db.session.commit()

    lower_msg = user_message.lower().strip()

    greetings = [
        "hi", "hii", "hello", "hey", "hai", "vanakkam",
        "good morning", "good afternoon", "good evening"
    ]

    try:
        if lower_msg in greetings:
            ai_response = (
                '<p>👋 Hey! I’m <strong>CeraAI</strong>.</p>'
                '<p>Tell me what you’re feeling or what health doubt you have. I’ll guide you clearly.</p>'
            )
        else:
            prompt_message = f"""
User question: {user_message}

Answer like CeraAI.

Rules:
- Give a clear and detailed health awareness answer.
- Do not give very short answers.
- Use simple English.
- Use HTML format only: <p>, <strong>, <ul>, <li>.
- Explain the issue clearly.
- Include possible reasons.
- Include what the user can do now.
- Include food/rest tips if useful.
- Include when to see a doctor.
- End with one follow-up question.
- Do not give diagnosis.
- Do not say you are a doctor.
"""

            ai_response = generate_response(conversation_id, prompt_message, language)

        ai_response = str(ai_response).strip()

    except Exception:
        ai_response = (
            "<p>Sorry, response generate panna konjam problem.</p>"
            "<p>Please try again.</p>"
        )

    bot_chat = ChatHistory(
        message=ai_response,
        sender='bot',
        conversation_id=conversation_id
    )

    db.session.add(bot_chat)
    db.session.commit()

    return jsonify({
        'response': ai_response,
        'language': language,
        'conversation_id': conversation_id
    })