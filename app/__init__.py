import os
import json
from datetime import datetime
from flask import Flask
from app.models import db, User, Post
from dotenv import load_dotenv

def create_app():
    app = Flask(__name__, 
                static_folder='static',
                template_folder='templates')
    
    load_dotenv()

    # --- Configuration ---
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///project.db")
    if app.config["SQLALCHEMY_DATABASE_URI"].startswith("postgres://"):
        app.config["SQLALCHEMY_DATABASE_URI"] = app.config["SQLALCHEMY_DATABASE_URI"].replace("postgres://", "postgresql://", 1)
    
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    
    # File upload settings
    UPLOAD_FOLDER = os.path.join(app.root_path, "static/uploads")
    AVATARS_FOLDER = os.path.join(app.root_path, "static/avatars")
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(AVATARS_FOLDER, exist_ok=True)
    
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
    app.config["AVATARS_FOLDER"] = AVATARS_FOLDER
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

    # --- Initialize Extensions ---
    db.init_app(app)

    # --- Register Blueprints ---
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.posts import posts_bp
    from app.routes.admin import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(posts_bp, url_prefix='/api/posts')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # --- Database Initialization ---
    with app.app_context():
        db.create_all()
        init_db_from_json()

    return app

def init_db_from_json():
    """
    JSONファイルからデータを読み込み、データベースを初期化する
    """
    # ユーザーデータ移行
    users_json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data/users.json")
    if os.path.exists(users_json_path):
        if User.query.first() is None:
            print("Migrating users from users.json to database...")
            with open(users_json_path, "r", encoding="utf-8") as f:
                users_data = json.load(f)
                for user_data in users_data:
                    new_user = User(
                        email=user_data["email"],
                        password_hash=user_data["password_hash"],
                        icon=user_data.get("icon", ""),
                        created_at=datetime.fromisoformat(user_data["created_at"]),
                    )
                    db.session.add(new_user)
            db.session.commit()
            print("User migration complete.")

    # 投稿データ移行
    posts_json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data/posts.json")
    if os.path.exists(posts_json_path):
        if Post.query.first() is None:
            print("Migrating posts from posts.json to database...")
            with open(posts_json_path, "r", encoding="utf-8") as f:
                posts_data = json.load(f)
                first_user = User.query.first()
                if first_user:
                    for post_data in posts_data:
                        new_post = Post(
                            title=post_data["title"],
                            description=post_data.get("description", ""),
                            image=post_data.get("image", ""),
                            timestamp=datetime.fromisoformat(post_data["timestamp"]),
                            user_id=first_user.id,
                        )
                        db.session.add(new_post)
            db.session.commit()
            print("Post migration complete.")
