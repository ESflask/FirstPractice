import json
import os
from datetime import datetime

import firebase_admin
from dotenv import load_dotenv
from firebase_admin import credentials, firestore
from flask import Flask


def create_app():
    app = Flask(__name__, static_folder="static", template_folder="templates")

    load_dotenv()

    app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")

    # File upload settings
    UPLOAD_FOLDER = os.path.join(app.root_path, "static/uploads")
    AVATARS_FOLDER = os.path.join(app.root_path, "static/avatars")
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(AVATARS_FOLDER, exist_ok=True)

    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
    app.config["AVATARS_FOLDER"] = AVATARS_FOLDER
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

    # --- Initialize Firebase ---
    # Check if already initialized to avoid error on reload
    if not firebase_admin._apps:
        # Check if serviceAccountKey.json exists
        key_path = "serviceAccountKey.json"
        if os.path.exists(key_path):
            cred = credentials.Certificate(key_path)
            firebase_admin.initialize_app(
                cred, {"storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET")}
            )
            print("Firebase Admin SDK initialized successfully.")
        else:
            print(
                "WARNING: serviceAccountKey.json not found. Firebase features will not work on server-side."
            )
            # Optionally initialize with default creds if on Google Cloud environment
            # firebase_admin.initialize_app()

    # Initialize Firestore Client
    try:
        app.db = firestore.client()
    except Exception as e:
        print(f"Failed to initialize Firestore client: {e}")
        app.db = None

    # --- Register Blueprints ---
    from app.routes.admin import admin_bp
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.posts import posts_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(posts_bp, url_prefix="/api/posts")
    app.register_blueprint(admin_bp, url_prefix="/admin")

    return app
