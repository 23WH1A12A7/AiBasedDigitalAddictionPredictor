from datetime import datetime, timedelta

from flask import Blueprint, jsonify, request, session
import sqlite3

from database import db
from utils.auth import token_required

wellness_bp = Blueprint("wellness_api", __name__)


def require_session_user():
    user_id = session.get("user_id")
    if not user_id:
        return None, (jsonify({"error": "User not logged in"}), 401)
    db.get_or_create_user(user_id)
    return user_id, None


@wellness_bp.route("/api/tasks", methods=["GET"])
@token_required
def get_tasks():
    tasks = db.get_wellness_tasks(request.user_id)
    return jsonify({"tasks": tasks, "total": len(tasks)}), 200


@wellness_bp.route("/api/tasks", methods=["POST"])
@token_required
def complete_task_with_token():
    data = request.get_json() or {}
    task_name = data.get("task_name")
    points = int(data.get("points", 10))
    if not task_name:
        return jsonify({"error": "task_name is required"}), 400
    db.save_wellness_task(request.user_id, task_name, points, completed=True)
    return jsonify({"success": True}), 200


@wellness_bp.route("/api/complete-task-session", methods=["POST"])
def complete_task_session():
    user_id, error = require_session_user()
    if error:
        return error

    data = request.get_json() or {}
    task_name = data.get("task_name")
    points = int(data.get("points", 10))
    if not task_name:
        return jsonify({"error": "task_name is required"}), 400

    db.save_wellness_task(user_id, task_name, points, completed=True)
    unlocked = db.check_and_unlock_achievements(user_id)
    metrics = db.get_dashboard_metrics(user_id)
    streak_data = db.get_streak_data(user_id)
    points_data = db.get_user_points(user_id)
    daily_completion = db.get_daily_task_completion(user_id, 6)

    return jsonify(
        {
            "success": True,
            "points_earned": points,
            "total_points": points_data["total_points"],
            "this_week": points_data["this_week"],
            "current_streak": streak_data["current_streak"],
            "completion_rate": daily_completion["completion_rate"],
            "daily_completion_rate": daily_completion["completion_rate"],
            "daily_tasks_completed": daily_completion["completed_tasks"],
            "daily_total_tasks": daily_completion["total_tasks"],
            "unlocked_achievements": unlocked,
            "wellbeing_score": metrics["wellbeing_score"],
        }
    )


@wellness_bp.route("/api/wellness-tasks", methods=["GET", "POST"])
def wellness_tasks():
    user_id, error = require_session_user()
    if error:
        return error

    if request.method == "POST":
        data = request.get_json() or {}
        task_name = data.get("task_id") or data.get("task_name")
        points = int(data.get("points", 10))
        completed = bool(data.get("completed", True))
        if not task_name:
            return jsonify({"error": "task_name or task_id is required"}), 400

        db.save_wellness_task(user_id, task_name, points, completed)
        streak_data = db.get_streak_data(user_id)
        metrics = db.get_dashboard_metrics(user_id)
        points_data = db.get_user_points(user_id)
        daily_completion = db.get_daily_task_completion(user_id, 6)
        return jsonify(
            {
                "success": True,
                "points_earned": points,
                "total_points": points_data["total_points"],
                "streak": streak_data["current_streak"],
                "completion_rate": daily_completion["completion_rate"],
                "daily_completion_rate": daily_completion["completion_rate"],
                "daily_tasks_completed": daily_completion["completed_tasks"],
                "daily_total_tasks": daily_completion["total_tasks"],
                "wellbeing_score": metrics["wellbeing_score"],
            }
        )

    return jsonify({"tasks": db.get_wellness_tasks(user_id)}), 200


@wellness_bp.route("/api/data/screen-time", methods=["POST"])
@token_required
def record_screen_time():
    data = request.get_json() or {}
    db.save_screen_time(
        request.user_id,
        float(data.get("hours", 0)),
        int(data.get("app_sessions", 0)),
        int(data.get("notifications", 0)),
        float(data.get("night_usage", 0)),
    )
    return jsonify({"success": True, "message": "Screen time recorded"}), 200


@wellness_bp.route("/api/data/sleep", methods=["POST"])
@token_required
def record_sleep():
    data = request.get_json() or {}
    db.save_sleep_data(
        request.user_id,
        float(data.get("hours_slept", data.get("hours", 0))),
        float(data.get("quality_score", 5)),
        data.get("bedtime"),
        data.get("wake_time"),
    )
    return jsonify({"success": True, "message": "Sleep data recorded"}), 200


@wellness_bp.route("/api/data/mood", methods=["POST"])
@token_required
def record_mood():
    data = request.get_json() or {}
    db.save_mood_entry(request.user_id, data.get("mood", "balanced"), float(data.get("mood_score", 3)), data.get("note"))
    return jsonify({"success": True, "message": "Mood data recorded"}), 200


@wellness_bp.route("/api/save-mood", methods=["POST"])
def save_mood():
    user_id, error = require_session_user()
    if error:
        return error
    data = request.get_json() or {}
    mood = data.get("mood", "")
    mood_score_map = {
        "amazing": 5.0,
        "good": 4.0,
        "okay": 3.0,
        "low": 2.0,
        "struggling": 1.0,
    }
    success = db.upsert_daily_mood_status(user_id, mood, mood_score_map.get(mood, 3.0), data.get("note", ""))
    if not success:
        return jsonify({"error": "Failed to save mood"}), 500
    streak_data = db.get_streak_data(user_id)
    daily_completion = db.get_daily_task_completion(user_id, 6)
    today_mood = db.get_today_mood_status(user_id)
    return jsonify(
        {
            "success": True,
            "streak": streak_data["current_streak"],
            "completion_rate": daily_completion["completion_rate"],
            "daily_completion_rate": daily_completion["completion_rate"],
            "today_mood": today_mood,
        }
    )


@wellness_bp.route("/api/streak-data")
def streak_data():
    user_id, error = require_session_user()
    if error:
        return error
    return jsonify(db.get_streak_data(user_id))


@wellness_bp.route("/api/today-completed-tasks")
def completed_tasks():
    user_id, error = require_session_user()
    if error:
        return error
    conn = sqlite3.connect(db.db_path)
    cursor = conn.cursor()
    cursor.execute(
        '''
        SELECT DISTINCT task_name FROM user_tasks
        WHERE user_id = ? AND completed = 1 AND date = date('now')
        ''',
        (user_id,),
    )
    tasks = [row[0] for row in cursor.fetchall()]
    conn.close()
    return jsonify({"completed_tasks": tasks})


@wellness_bp.route("/api/trends", methods=["GET"])
def get_trends():
    user_id, error = require_session_user()
    if error:
        return error

    conn = sqlite3.connect(db.db_path)
    cursor = conn.cursor()
    today = datetime.now().date()
    this_week_start = today - timedelta(days=today.weekday())
    last_week_start = this_week_start - timedelta(days=7)
    last_week_end = this_week_start - timedelta(days=1)

    cursor.execute("SELECT AVG(mood_score) FROM mood_entries WHERE user_id = ? AND DATE(created_at) >= ?", (user_id, this_week_start))
    this_week_mood = cursor.fetchone()[0] or 0
    cursor.execute(
        "SELECT AVG(mood_score) FROM mood_entries WHERE user_id = ? AND DATE(created_at) >= ? AND DATE(created_at) <= ?",
        (user_id, last_week_start, last_week_end),
    )
    last_week_mood = cursor.fetchone()[0] or 0
    cursor.execute("SELECT AVG(hours) FROM screen_time WHERE user_id = ? AND date >= ?", (user_id, this_week_start))
    this_week_screen = cursor.fetchone()[0] or 0
    cursor.execute(
        "SELECT AVG(hours) FROM screen_time WHERE user_id = ? AND date >= ? AND date <= ?",
        (user_id, last_week_start, last_week_end),
    )
    last_week_screen = cursor.fetchone()[0] or 0
    cursor.execute("SELECT COUNT(*) FROM user_tasks WHERE user_id = ? AND completed = 1 AND date >= ?", (user_id, this_week_start))
    this_week_tasks = cursor.fetchone()[0] or 0
    cursor.execute(
        "SELECT COUNT(*) FROM user_tasks WHERE user_id = ? AND completed = 1 AND date >= ? AND date <= ?",
        (user_id, last_week_start, last_week_end),
    )
    last_week_tasks = cursor.fetchone()[0] or 0
    conn.close()

    mood_trend = int(((this_week_mood - last_week_mood) / last_week_mood) * 100) if last_week_mood else 0
    energy_trend = int(((last_week_screen - this_week_screen) / last_week_screen) * 100) if last_week_screen else 0
    focus_trend = int(((this_week_tasks - last_week_tasks) / last_week_tasks) * 100) if last_week_tasks else (100 if this_week_tasks else 0)

    return jsonify({"mood": mood_trend, "energy": energy_trend, "focus": focus_trend})
