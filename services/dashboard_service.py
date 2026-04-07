from database import db


def build_dashboard_payload(user_id: str, period: str = "7days"):
    db.get_or_create_user(user_id)

    days = 7
    period_value = (period or "7days").lower()
    if "30" in period_value or "month" in period_value:
        days = 30
    elif "90" in period_value or "3" in period_value:
        days = 90

    metrics = db.get_dashboard_metrics(user_id)
    risk_data = db.calculate_addiction_risk(user_id)
    streak_data = db.get_streak_data(user_id)
    points_data = db.get_user_points(user_id)
    db.check_and_unlock_achievements(user_id)
    achievements = db.get_user_achievements(user_id)
    historical_data = db.get_historical_data(user_id, days)
    activity_summary = db.get_task_summary(user_id)
    completion_summary = db.get_completion_summary(user_id, days if days <= 30 else 30)
    daily_completion = db.get_daily_task_completion(user_id, 6)

    unlocked = [achievement for achievement in achievements if achievement["unlocked"]]

    return {
        "session_data": {
            "risk": risk_data["level"],
            "risk_score": risk_data["score"],
            "confidence": metrics.get("wellbeing_score", 50),
            "risk_factors": risk_data["factors"],
            "usage_data": {
                "daily_screen_time": metrics.get("daily_screen_time", 0),
                "night_usage": round((metrics.get("daily_screen_time", 0) or 0) * 0.3, 1),
            },
            "mood_analysis": {
                "avg_mood_score": metrics.get("avg_mood", 3),
                "stress_level": "High"
                if metrics.get("avg_mood", 3) < 2.5
                else "Moderate"
                if metrics.get("avg_mood", 3) < 3.5
                else "Low",
                "sleep_hours": risk_data.get("avg_sleep", 0),
                "sleep_quality": risk_data.get("avg_sleep", 0) > 7,
            },
        },
        "historical_data": historical_data,
        "period": f"{days} days",
        "user_id": user_id,
        "wellbeing_score": metrics.get("wellbeing_score", 50),
        "current_streak": streak_data.get("current_streak", 0),
        "achievement_count": len(unlocked),
        "total_points": points_data.get("total_points", 0),
        "completion_rate": daily_completion.get("completion_rate", 0),
        "daily_tasks": activity_summary.get("daily_tasks", 0),
        "mood_checkins": activity_summary.get("mood_checkins", 0),
        "active_days": streak_data.get("active_days", 0),
        "tasks_completed": completion_summary.get("completed_tasks", 0),
        "daily_tasks_completed": daily_completion.get("completed_tasks", 0),
        "daily_total_tasks": daily_completion.get("total_tasks", 6),
        "points_this_week": points_data.get("this_week", 0),
    }


def build_insights(user_id: str):
    metrics = db.get_dashboard_metrics(user_id)
    risk_data = db.calculate_addiction_risk(user_id)
    mood_score = metrics.get("avg_mood", 3)

    return [
        {
            "title": "Screen Time Awareness" if risk_data["level"] in {"Critical", "High"} else "Healthy Digital Balance",
            "description": (
                f"Average screen time is {risk_data['avg_screen_time']}h/day. Aim to reduce it gradually this week."
                if risk_data["level"] in {"Critical", "High"}
                else f"Your screen time is trending in a healthy range at {risk_data['avg_screen_time']}h/day."
            ),
            "status": "Needs Attention" if risk_data["level"] in {"Critical", "High"} else "Healthy",
            "status_type": "warning" if risk_data["level"] in {"Critical", "High"} else "positive",
            "metrics": [
                {"label": "Screen Time", "value": f"{risk_data['avg_screen_time']}h/day"},
                {"label": "Risk", "value": risk_data["level"]},
            ],
        },
        {
            "title": "Sleep Needs Support" if risk_data["avg_sleep"] < 6 else "Sleep Progress",
            "description": (
                f"Average sleep is {risk_data['avg_sleep']}h. Earlier device cutoff times should help."
                if risk_data["avg_sleep"] < 6
                else f"Sleep duration is averaging {risk_data['avg_sleep']}h. Keep that bedtime routine steady."
            ),
            "status": "Needs Improvement" if risk_data["avg_sleep"] < 6 else "Excellent",
            "status_type": "warning" if risk_data["avg_sleep"] < 6 else "positive",
            "metrics": [
                {"label": "Sleep", "value": f"{risk_data['avg_sleep']}h"},
                {"label": "Target", "value": "7-9h"},
            ],
        },
        {
            "title": "Emotional Wellbeing",
            "description": (
                "Mood check-ins are helping build a more accurate wellness picture."
                if mood_score >= 3.5
                else "More mood check-ins and small recovery habits can help improve your trend."
            ),
            "status": "Balanced" if mood_score >= 3.5 else "Support Needed",
            "status_type": "positive" if mood_score >= 3.5 else "danger",
            "metrics": [
                {"label": "Mood Score", "value": f"{mood_score}/5"},
                {"label": "Trend", "value": "Stable" if mood_score >= 3.5 else "Watch closely"},
            ],
        },
    ]
