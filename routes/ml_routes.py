import random

from flask import Blueprint, jsonify, render_template, request, session

from database import db
from psychological_module import PsychologicalAnalyzer
from services.ml_service import predict_addiction

ml_bp = Blueprint("ml", __name__)
psych_analyzer = PsychologicalAnalyzer()
user_sessions = {}


def calculate_mood_score(_data):
    data = _data or {}
    mood_value = 6 - int(data.get("social_media_feeling", 3) or 3)
    sleep_value = 6 - int(data.get("sleep_quality", 3) or 3)
    focus_value = 6 - int(data.get("concentration", 3) or 3)
    distraction_value = 6 - int(data.get("distraction_frequency", 3) or 3)
    night_value = 6 - int(data.get("night_usage", 3) or 3)
    screen_value = 6 - int(data.get("daily_screen_time", 3) or 3)

    weighted_average = (
        mood_value * 0.24 +
        sleep_value * 0.2 +
        focus_value * 0.18 +
        distraction_value * 0.16 +
        night_value * 0.12 +
        screen_value * 0.1
    )
    return round(max(1.0, min(5.0, weighted_average)), 1)


def determine_emotional_state(score):
    if score >= 4.5:
        return "Excellent"
    if score >= 3.5:
        return "Good"
    if score >= 2.5:
        return "Balanced"
    return "Needs Attention"


def generate_insights(_data):
    data = _data or {}
    insights = []
    if int(data.get("daily_screen_time", 3) or 3) >= 4:
        insights.append("Your current phone usage pattern is higher than ideal for steady focus.")
    else:
        insights.append("Your screen time pattern is within a manageable range.")

    if int(data.get("sleep_quality", 3) or 3) >= 4:
        insights.append("Sleep quality looks like a major factor behind your mood and concentration.")
    else:
        insights.append("Sleep habits are reasonably supportive of your wellbeing.")

    if int(data.get("distraction_frequency", 3) or 3) >= 4:
        insights.append("Frequent distractions suggest you may benefit from shorter focused sessions.")
    else:
        insights.append("Your attention pattern suggests good potential for structured study blocks.")

    return insights


def generate_recommendations(_data):
    data = _data or {}
    recommendations = []

    if int(data.get("night_usage", 3) or 3) >= 4:
        recommendations.append("Set a no-phone rule for the last 45 minutes before sleep.")
    if int(data.get("daily_screen_time", 3) or 3) >= 4:
        recommendations.append("Reduce one daily screen-time block by 30 minutes this week.")
    if int(data.get("concentration", 3) or 3) >= 4 or int(data.get("distraction_frequency", 3) or 3) >= 4:
        recommendations.append("Use a 25-minute focus timer followed by a 5-minute recovery break.")
    if int(data.get("social_media_feeling", 3) or 3) >= 4:
        recommendations.append("Replace one social media session with an offline activity or conversation.")
    if not recommendations:
        recommendations.append("Keep tracking your habits daily to maintain your current balance.")

    return recommendations[:3]


@ml_bp.route("/api/mood-analysis", methods=["POST"])
def api_mood_analysis():
    data = request.get_json() or {}
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "User not logged in"}), 401

    db.get_or_create_user(user_id)
    screen_map = {1: 1.5, 2: 3.5, 3: 5.5, 4: 7.5, 5: 10.0}
    sleep_map = {1: 9, 2: 8, 3: 7, 4: 6, 5: 4}
    daily_screen_value = int(data.get("daily_screen_time", 3))
    sleep_quality_value = int(data.get("sleep_quality", 3))
    screen_time_hours = screen_map.get(daily_screen_value, 5.5)
    sleep_hours = sleep_map.get(sleep_quality_value, 7)
    mood_score = calculate_mood_score(data)

    mood_saved = db.save_mood_entry(user_id, data.get("mood", "balanced"), mood_score, data.get("note", ""))
    screen_saved = db.save_screen_time(user_id, screen_time_hours, data.get("app_sessions", 0), data.get("notifications", 0), data.get("night_usage", 0))
    sleep_saved = db.save_sleep_data(user_id, sleep_hours, sleep_quality_value)
    new_achievements = db.check_and_unlock_achievements(user_id)
    risk_data = db.calculate_addiction_risk(user_id)
    streak_data = db.get_streak_data(user_id)

    if mood_score >= 4.2:
        trend = "Improving"
    elif mood_score >= 3.2:
        trend = "Stable"
    else:
        trend = "Needs Support"

    return jsonify(
        {
            "mood_score": mood_score,
            "emotional_state": determine_emotional_state(mood_score),
            "risk_level": risk_data["level"],
            "risk_score": risk_data.get("score", 0),
            "risk_factors": risk_data.get("factors", []),
            "trend": trend,
            "insights": generate_insights(data),
            "recommendations": generate_recommendations(data),
            "streak_updated": True,
            "current_streak": streak_data.get("current_streak", 0),
            "completion_rate": streak_data.get("completion_rate", 0),
            "new_achievements": new_achievements,
            "data_saved": {"mood": mood_saved, "screen_time": screen_saved, "sleep": sleep_saved},
        }
    )


@ml_bp.route("/predict", methods=["POST"])
def predict():
    if "user_id" not in session:
        session["user_id"] = f"user_{random.randint(1000, 9999)}"
        session.permanent = True

    if request.form.get("source") == "ai_guided":
        payload = {
            "daily_screen_time": request.form.get("daily_screen_time", 5),
            "gaming_time": request.form.get("gaming_time", 2),
            "social_media_usage": request.form.get("social_media_usage", 3),
            "app_sessions": request.form.get("app_sessions", 50),
            "notifications": request.form.get("notifications", 100),
            "night_usage": request.form.get("night_usage", 2),
        }
    else:
        payload = {
            "daily_screen_time": request.form["daily_screen_time"],
            "gaming_time": request.form["gaming_time"],
            "social_media_usage": request.form["social_media_usage"],
            "app_sessions": request.form["app_sessions"],
            "notifications": request.form["notifications"],
            "night_usage": request.form["night_usage"],
        }

    result = predict_addiction(payload)
    session_id = str(random.randint(1000, 9999))
    user_sessions[session_id] = {**result, "usage_data": payload}
    db.get_or_create_user(session["user_id"])
    db.save_screen_time(session["user_id"], float(payload["daily_screen_time"]), int(float(payload["app_sessions"])), int(float(payload["notifications"])), float(payload["night_usage"]))

    return render_template("ai_guided_home.html", prediction_text=result["prediction_text"], confidence=result["confidence"], risk=result["risk"], session_id=session_id)


@ml_bp.route("/analyze-mood", methods=["POST"])
def analyze_mood():
    responses = [
        request.form.get("anxiety_without_phone"),
        request.form.get("loneliness_after_social"),
        request.form.get("mood_impact"),
        request.form.get("stress_after_usage"),
        request.form.get("concentration_level"),
    ]
    session_id = request.form.get("session_id", "default")
    analysis = psych_analyzer.analyze_mood_responses(responses)
    if not analysis:
        return render_template("mood_analysis_new.html", error="Invalid responses. Please ensure all fields are filled correctly.")

    tips = psych_analyzer.get_personalized_tips(analysis)
    suggestions = psych_analyzer.get_interaction_suggestions(analysis)
    if session_id in user_sessions:
        user_sessions[session_id]["mood_analysis"] = analysis
        user_sessions[session_id]["tips"] = tips
        user_sessions[session_id]["suggestions"] = suggestions

    return render_template("mood_analysis_new.html", analysis=analysis, tips=tips, suggestions=suggestions, session_id=session_id)


@ml_bp.route("/detox-plans")
def detox_plans():
    return render_template("detox_plans.html", plans=psych_analyzer.generate_digital_detox_plans())
