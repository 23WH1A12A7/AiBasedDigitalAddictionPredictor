from datetime import datetime

from flask import Blueprint, jsonify, request

from database import db
from services.dashboard_service import build_dashboard_payload, build_insights
from utils.auth import get_request_user_id

dashboard_bp = Blueprint("dashboard_api", __name__)


@dashboard_bp.route("/api/dashboard-data", methods=["GET"])
def get_dashboard_data():
    user_id = get_request_user_id()
    if not user_id:
        return jsonify({"error": "User not logged in"}), 401
    return jsonify(build_dashboard_payload(user_id, request.args.get("period", "7days"))), 200


@dashboard_bp.route("/api/quick-stats", methods=["GET"])
def get_quick_stats():
    user_id = get_request_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    metrics = db.get_dashboard_metrics(user_id)
    streak_data = db.get_streak_data(user_id)
    points_data = db.get_user_points(user_id)
    activity_summary = db.get_task_summary(user_id)
    daily_completion = db.get_daily_task_completion(user_id, 6)

    return jsonify(
        {
            "wellbeing_score": metrics.get("wellbeing_score", 50),
            "current_streak": streak_data.get("current_streak", 0),
            "longest_streak": streak_data.get("longest_streak", 0),
            "completion_rate": daily_completion.get("completion_rate", 0),
            "total_points": points_data.get("total_points", 0),
            "points_this_week": points_data.get("this_week", 0),
            "daily_screen_time": round(metrics.get("daily_screen_time", 0), 1),
            "daily_tasks": activity_summary.get("daily_tasks", 0),
            "daily_tasks_completed": daily_completion.get("completed_tasks", 0),
            "daily_total_tasks": daily_completion.get("total_tasks", 6),
            "mood_checkins": activity_summary.get("mood_checkins", 0),
        }
    )


@dashboard_bp.route("/api/achievements", methods=["GET"])
def get_achievements():
    user_id = get_request_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    db.check_and_unlock_achievements(user_id)
    achievements = db.get_user_achievements(user_id)
    daily_completion = db.get_daily_task_completion(user_id, 6)
    streak_data = db.get_streak_data(user_id)
    metrics = db.get_dashboard_metrics(user_id)

    for achievement in achievements:
        if achievement["id"] == "task_starter":
            achievement["description"] = f"Unlocked at 5 wellness tasks. Current completed today: {daily_completion['completed_tasks']}/6"
        elif achievement["id"] == "task_master":
            achievement["description"] = f"Unlocked at 10 completed tasks. Current weekly total: {streak_data.get('tasks_completed', 0)}"
        elif achievement["id"] == "week_warrior":
            achievement["description"] = f"Unlocked at a 7-day streak. Current streak: {streak_data.get('current_streak', 0)}"
        elif achievement["id"] == "balance_score":
            achievement["description"] = f"Unlocked at 80+ wellbeing score. Current score: {metrics.get('wellbeing_score', 0)}"

    unlocked = [achievement for achievement in achievements if achievement["unlocked"]]
    locked = [achievement for achievement in achievements if not achievement["unlocked"]]
    return jsonify(unlocked + locked[:2]), 200


@dashboard_bp.route("/api/goals", methods=["GET"])
def get_goals():
    user_id = get_request_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    return jsonify(db.calculate_goal_progress(user_id)), 200


@dashboard_bp.route("/api/insights", methods=["GET"])
def get_insights():
    user_id = get_request_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    return jsonify(build_insights(user_id)), 200


@dashboard_bp.route("/api/export-data", methods=["GET"])
def export_data():
    user_id = get_request_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    user = db.get_user_by_id(user_id) or {}
    payload = build_dashboard_payload(user_id, request.args.get("period", "30days"))
    export_payload = {
        "exported_at": datetime.now().isoformat(),
        "user": {
            "id": user.get("user_id"),
            "name": user.get("username", ""),
            "email": user.get("email", ""),
            "auth_provider": user.get("auth_provider", "local"),
        },
        "today_mood": db.get_today_mood_status(user_id),
        "points_breakdown": db.get_points_breakdown(user_id, 7),
        "streak_data": db.get_streak_data(user_id),
        "dashboard": payload,
        "achievements": db.get_user_achievements(user_id),
        "goals": db.calculate_goal_progress(user_id),
        "insights": build_insights(user_id),
    }
    return jsonify(export_payload), 200
