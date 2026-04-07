from flask import Blueprint, redirect, render_template, request, session, url_for

from database import db
from utils.auth import login_required

pages_bp = Blueprint("pages", __name__)


@pages_bp.route("/")
def home():
    return render_template("beautiful_home.html")


@pages_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard_new.html")


@pages_bp.route("/wellness")
@login_required
def wellness():
    return render_template("wellness_new.html")


@pages_bp.route("/mood-analysis")
@login_required
def mood_analysis():
    return render_template("mood_analysis_new.html")


@pages_bp.route("/profile")
@login_required
def profile():
    user_id = session.get("user_id")
    user = db.get_user_by_id(user_id)
    return render_template(
        "profile.html",
        user=user,
        today_mood=db.get_today_mood_status(user_id),
        saved_mood_count=db.get_saved_mood_count(user_id),
        points_breakdown=db.get_points_breakdown(user_id, 7),
        streak_data=db.get_streak_data(user_id),
        profile_message=request.args.get("message"),
        profile_error=request.args.get("error"),
        is_firebase_user=(user or {}).get("auth_provider") == "firebase",
    )


@pages_bp.route("/profile/update", methods=["POST"])
@login_required
def update_profile():
    user_id = session.get("user_id")
    success, message = db.update_profile(
        user_id,
        request.form.get("username", ""),
        request.form.get("email", ""),
        request.form.get("profile_photo_data", ""),
    )
    if success:
        user = db.get_user_by_id(user_id)
        session["username"] = user.get("username", "")
        session["email"] = user.get("email", "")
        session["profile_photo"] = user.get("profile_photo", "")
        return redirect(url_for("pages.profile", message=message))
    return redirect(url_for("pages.profile", error=message))


@pages_bp.route("/profile/password", methods=["POST"])
@login_required
def change_password():
    user_id = session.get("user_id")
    new_password = request.form.get("new_password", "")
    confirm_password = request.form.get("confirm_password", "")
    if len(new_password) < 6:
        return redirect(url_for("pages.profile", error="New password must be at least 6 characters"))
    if new_password != confirm_password:
        return redirect(url_for("pages.profile", error="New password and confirm password must match"))

    success, message = db.change_password(
        user_id,
        request.form.get("current_password", ""),
        new_password,
    )
    if success:
        return redirect(url_for("pages.profile", message=message))
    return redirect(url_for("pages.profile", error=message))
