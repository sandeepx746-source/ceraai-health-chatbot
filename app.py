from dotenv import load_dotenv
load_dotenv()

import os
import requests
from flask import Flask, jsonify

from config import Config
from database.db import db, login_manager


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)

    from routes.auth_routes import auth_bp
    from routes.chatbot_routes import chatbot_bp
    from routes.views_routes import views_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(chatbot_bp)
    app.register_blueprint(views_bp)

    @app.route("/api/health-news")
    def health_news():
        try:
            api_key = os.getenv("GNEWS_API_KEY")

            if not api_key:
                return jsonify({
                    "success": False,
                    "error": "GNEWS_API_KEY missing in .env"
                }), 500

            url = "https://gnews.io/api/v4/top-headlines"

            params = {
                "apikey": api_key,
                "category": "health",
                "country": "in",
                "lang": "en",
                "max": 10
            }

            res = requests.get(url, params=params, timeout=10)
            data = res.json()

            if res.status_code != 200:
                return jsonify({
                    "success": False,
                    "error": data
                }), 500

            articles = []

            for item in data.get("articles", []):
                articles.append({
                    "title": item.get("title", "No title"),
                    "description": item.get("description") or "",
                    "link": item.get("url") or "#",
                    "image": item.get("image") or "",
                    "source": item.get("source", {}).get("name", "Health News"),
                    "publishedAt": item.get("publishedAt", "")
                })

                if len(articles) == 10:
                    break

            return jsonify({
                "success": True,
                "count": len(articles),
                "articles": articles
            })

        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500

    with app.app_context():
        db.create_all()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5001, debug=True)