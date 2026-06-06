from flask import Blueprint, render_template, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from database.models import ChatHistory, Conversation
import os
import json
import ssl
import urllib.request
import urllib.error

views_bp = Blueprint('views', __name__)


# ==============================
# 🔥 CERA AI VOICE FUNCTION (FIXED + HUMAN)
# ==============================
def get_voice_ai_response(user_message):

    api_key = os.getenv("GROQ_API_KEY") or os.getenv("GROK_API_KEY")

    print("API KEY =", api_key[:10] if api_key else "NOT FOUND")

    if not api_key:
        return "API key missing. Please check .env file."

    # ==============================
    # 🔥 SMART LANGUAGE PROMPT (FIXED)
    # ==============================
    prompt = f"""
You are CeraAI, a real-time medical voice assistant.

🚨 LANGUAGE RULE (VERY IMPORTANT):
- If user speaks English → reply ONLY in SIMPLE English.
- If user speaks Tamil or Tanglish → reply ONLY in NATURAL SPOKEN Tamil.
- NEVER mix languages.

🚨 VOICE STYLE RULE:
- Speak like a REAL doctor talking casually to a patient.
- Very natural spoken tone.
- No formal textbook language.

🚨 LENGTH RULE:
- ONLY 2–4 short sentences max.
- No paragraphs.
- No bullet points.

🚨 STRUCTURE:
1. Simple reason
2. What to do now
3. When to see doctor (if needed)

User: {user_message}
"""

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {
                "role": "system",
                "content": "You are CeraAI. Detect language and respond naturally like a real doctor in same language."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.7,
        "max_tokens": 140
    }

    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0"
        },
        method="POST"
    )

    try:
        context = ssl._create_unverified_context()

        with urllib.request.urlopen(req, timeout=25, context=context) as response:
            result = json.loads(response.read().decode("utf-8"))
            return result["choices"][0]["message"]["content"]

    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="ignore")

        print("VOICE AI ERROR:", e.code)
        print(error_body)

        if e.code == 401:
            return "Invalid API key."
        if e.code == 403:
            return "Access denied."
        if e.code == 429:
            return "Too many requests. Try again later."

        return "Server error."

    except Exception as e:
        print("Voice AI Error:", e)
        return "System error. Try again later."


# ==============================
# HOME ROUTE
# ==============================
@views_bp.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('views.chatbot'))
    return render_template('index.html')


# ==============================
# CHATBOT ROUTE
# ==============================
@views_bp.route('/chatbot', methods=['GET', 'POST'])
@views_bp.route('/chatbot/<int:conversation_id>', methods=['GET', 'POST'])
@login_required
def chatbot(conversation_id=None):

    if request.method == 'POST':
        data = request.get_json()
        user_message = data.get('message', '').strip()

        if not user_message:
            return jsonify({"response": "Please ask a question."})

        bot_reply = get_voice_ai_response(user_message)

        return jsonify({"response": bot_reply})

    conversations = Conversation.query.filter_by(
        user_id=current_user.id
    ).order_by(Conversation.timestamp.desc()).all()

    history = []

    if conversation_id:
        conv = Conversation.query.get_or_404(conversation_id)

        if conv.user_id != current_user.id:
            return "Unauthorized", 403

        history = ChatHistory.query.filter_by(
            conversation_id=conversation_id
        ).order_by(ChatHistory.timestamp.asc()).all()

    return render_template(
        'chatbot.html',
        conversations=conversations,
        history=history,
        current_conversation_id=conversation_id
    )


# ==============================
# DISEASE PAGE
# ==============================
@views_bp.route('/disease-awareness')
def disease_awareness():
    return render_template('disease_awareness.html')