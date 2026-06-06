import time
import requests
from config import Config


def query_grok(messages):
    api_key = Config.GROK_API_KEY

    if not api_key:
        return "<p>API key is missing.</p>"

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": messages,
        "temperature": 0.75,
        "max_tokens": 800
    }

    try:
        start = time.time()

        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=15
        )

        print("GROQ TIME:", round(time.time() - start, 2), "seconds")
        print("STATUS CODE:", response.status_code)

        if response.status_code != 200:
            print("RAW RESPONSE:", response.text)
            return f"<p>API Error {response.status_code}</p>"

        data = response.json()
        return data["choices"][0]["message"]["content"].strip()

    except requests.exceptions.Timeout:
        return "<p>Request timed out. Try again.</p>"

    except requests.exceptions.ConnectionError:
        return "<p>Internet connection error.</p>"

    except Exception as e:
        print("GROQ ERROR:", e)
        return "<p>Server Error</p>"