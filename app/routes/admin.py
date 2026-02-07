from flask import Blueprint, render_template, session, current_app
from app.utils.decorators import admin_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route("/")
@admin_required
def admin_dashboard():
    """
    管理ダッシュボード
    """
    user_id = session.get("user_id")
    if not user_id:
        return "Unauthorized", 401
    
    db = current_app.db
    user_data = {}
    if db:
        doc = db.collection('users').document(user_id).get()
        if doc.exists:
            user_data = doc.to_dict()
    
    return render_template("admin/index.html", current_user=user_data)


@admin_bp.route("/users")
@admin_required
def admin_users():
    """
    ユーザー管理ページ (仮)
    """
    return "<h1>User Management</h1><a href='/admin'>Back</a>"


@admin_bp.route("/posts")
@admin_required
def admin_posts():
    """
    投稿管理ページ (仮)
    """
    return "<h1>Post Management</h1><a href='/admin'>Back</a>"
