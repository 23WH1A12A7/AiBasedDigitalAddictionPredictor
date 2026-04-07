import logging
import os

from flask import Flask, session
from flask_cors import CORS
from dotenv import load_dotenv

from database import db
from routes.auth_routes import auth_bp
from routes.dashboard_routes import dashboard_bp
from routes.ml_routes import ml_bp
from routes.page_routes import pages_bp
from routes.wellness_routes import wellness_bp


def create_app():
    load_dotenv(".env.local")
    load_dotenv()
    app = Flask(__name__)
    app.secret_key = os.environ.get("SECRET_KEY", "your-secret-key-here-change-in-production")
    app.config["SECRET_KEY"] = app.secret_key
    app.config["JSON_SORT_KEYS"] = False
    app.config["MAX_CONTENT_LENGTH"] = 4 * 1024 * 1024
    CORS(app, supports_credentials=True)

    logging.basicConfig(level=logging.INFO)
    db.initialize_achievements()

    @app.context_processor
    def inject_app_context():
        saved_mood_count = 0
        if session.get("user_id"):
            try:
                saved_mood_count = db.get_saved_mood_count(session["user_id"])
            except Exception:
                saved_mood_count = 0
        return {
            "saved_mood_count": saved_mood_count,
        }

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(wellness_bp)
    app.register_blueprint(ml_bp)
    app.register_blueprint(pages_bp)
    return app
