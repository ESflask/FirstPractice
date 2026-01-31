from flask import Blueprint, render_template, session
from app.models import User
from app.utils.decorators import admin_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route("/")
@admin_required
def admin_dashboard():
    """
    管理ダッシュボード
    """
    user_id = session.get("user_id")
    user = User.query.get(user_id)
    return render_template("admin/index.html", current_user=user)


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
