from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from functools import wraps
import numpy as np
import pickle
import random
from datetime import datetime, timedelta
from database import db
import random
import joblib
import json
import sqlite3
from psychological_module import PsychologicalAnalyzer

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

model = joblib.load("random_forest_addiction_model.pkl")

psych_analyzer = PsychologicalAnalyzer()

user_sessions = {}

# Authentication routes
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        print(f"Login attempt - Username: {username}")
        
        try:
            user = db.authenticate_user(username, password)
            print(f"Authentication result: {user}")
            
            if user:
                session['user_id'] = user['user_id']
                session['username'] = user['username']
                session['email'] = user['email']
                session.permanent = True
                
                print(f"Session set: {dict(session)}")
                
                # Update last active
                db.update_last_active(user['user_id'])
                
                return redirect(url_for('home'))
            else:
                return render_template("login.html", error="Invalid username or password")
        except Exception as e:
            print(f"Login error: {e}")
            import traceback
            traceback.print_exc()
            return render_template("login.html", error="An error occurred. Please try again.")
    
    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        
        print(f"Signup attempt - Username: {username}, Email: {email}")
        
        try:
            # Basic validation
            if password != confirm_password:
                return render_template("signup.html", error="Passwords do not match")
            
            if len(password) < 6:
                return render_template("signup.html", error="Password must be at least 6 characters")
            
            if len(username) < 3:
                return render_template("signup.html", error="Username must be at least 3 characters")
            
            # Create user
            success = db.create_user(username, email, password)
            print(f"User creation result: {success}")
            
            if success:
                # Auto-login after successful signup
                user = db.authenticate_user(username, password)
                print(f"Auto-authentication result: {user}")
                if user:
                    session['user_id'] = user['user_id']
                    session['username'] = user['username']
                    session['email'] = user['email']
                    session.permanent = True
                    
                    print(f"Session set after signup: {dict(session)}")
                    
                    # Update last active
                    db.update_last_active(user['user_id'])
                    
                    return redirect(url_for('home'))
            else:
                return render_template("signup.html", error="Username or email already exists")
        except Exception as e:
            print(f"Signup error: {e}")
            import traceback
            traceback.print_exc()
            return render_template("signup.html", error="An error occurred. Please try again.")
    
    return render_template("signup.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/")
def home():
    # Direct access without authentication
    return render_template("beautiful_home.html")

@app.route("/mood-analysis")
def mood_analysis():
    # Create a session if not exists for demo purposes
    if 'user_id' not in session:
        session['user_id'] = f"demo_user_{random.randint(10000, 99999)}"
        session['username'] = "Demo User"
        session.permanent = True
    return render_template("mood_analysis_new.html")

@app.route("/dashboard")
def dashboard():
    # Create a session if not exists for demo purposes
    if 'user_id' not in session:
        session['user_id'] = f"demo_user_{random.randint(10000, 99999)}"
        session['username'] = "Demo User"
        session.permanent = True
    return render_template("dashboard_new.html")

@app.route("/wellness")
def wellness():
    # Create a session if not exists for demo purposes
    if 'user_id' not in session:
        session['user_id'] = f"demo_user_{random.randint(10000, 99999)}"
        session['username'] = "Demo User"
        session.permanent = True
    return render_template("wellness_new.html")

@app.route("/api/mood-analysis", methods=["POST"])
def api_mood_analysis():
    try:
        data = request.get_json()
        user_id = session.get('user_id', 'default_user')
        
        # Get or create user
        db.get_or_create_user(user_id)
        
        # Process mood analysis data
        mood_score = calculate_mood_score(data)
        emotional_state = determine_emotional_state(mood_score)
        risk_level = assess_risk_level(data)
        
        # Save mood entry to database
        mood_value = data.get('mood', 'balanced')
        note = data.get('note', '')
        db.save_mood_entry(user_id, mood_value, mood_score, note)
        
        result = {
            "mood_score": mood_score,
            "emotional_state": emotional_state,
            "risk_level": risk_level,
            "insights": generate_insights(data),
            "recommendations": generate_recommendations(data)
        }
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/dashboard-data/<session_id>")
@app.route("/api/dashboard-data/<session_id>/<period>")
def get_dashboard_data(session_id, period=None):
    try:
        user_id = session.get('user_id')
        if not user_id:
            # Try to use an existing user that has data
            try:
                conn = sqlite3.connect('wellness_data.db')
                cursor = conn.cursor()
                # Get today's date and find user with screen time data
                from datetime import datetime
                today = datetime.now().date()
                cursor.execute('''
                    SELECT user_id FROM screen_time 
                    WHERE date = ?
                    ORDER BY hours DESC 
                    LIMIT 1
                ''', (today,))
                result = cursor.fetchone()
                conn.close()
                
                if result:
                    user_id = result[0]
                    session['user_id'] = user_id
                    session.permanent = True
                    print(f"Using existing user with screen time data: {user_id}")
                else:
                    # Initialize session if no existing data found
                    user_id = f"user_{random.randint(10000, 99999)}"
                    session['user_id'] = user_id
                    session.permanent = True
                    print(f"Created new user: {user_id}")
            except Exception as e:
                print(f"Error getting existing user: {e}")
                user_id = f"user_{random.randint(10000, 99999)}"
                session['user_id'] = user_id
                session.permanent = True
        
        # Get or create user
        db.get_or_create_user(user_id)
        
        # Determine days based on period
        days = 7  # default
        if period:
            if '30' in period or 'month' in period.lower():
                days = 30
            elif '90' in period or '3' in period:
                days = 90
            elif 'week' in period.lower():
                days = 7
        
        # Get real dashboard metrics for the selected user
        metrics = db.get_dashboard_metrics(user_id)
        
        # Get historical data for specified period
        historical_data = db.get_historical_data(user_id, days)
        
        # Format dates based on period
        if days >= 30:
            # Show month names for longer periods
            historical_data = format_historical_data_for_month(historical_data)
        
        # Build session data with real metrics
        session_data = {
            "risk": "Medium" if metrics['wellbeing_score'] < 70 else "Low",
            "confidence": metrics['wellbeing_score'],
            "usage_data": {
                "daily_screen_time": metrics['daily_screen_time'],  # Real daily screen time
                "night_usage": metrics['daily_screen_time'] * 0.3  # Estimate
            },
            "mood_analysis": {
                "emotional_state": determine_emotional_state(metrics['avg_mood']),
                "stress_level": "Moderate",
                "phone_dependency": "Low",
                "sleep_impact": "Minimal"
            }
        }
        
        data = {
            "session_data": session_data,
            "historical_data": historical_data,
            "period": f"{days} days",
            "user_id": user_id  # Add for debugging
        }
        
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def format_historical_data_for_month(historical_data):
    """Format historical data to show month names for longer periods"""
    from datetime import datetime
    
    formatted_data = {}
    for key, data_points in historical_data.items():
        formatted_points = []
        for point in data_points:
            # Convert date to show month name
            if 'date' in point:
                try:
                    date_obj = datetime.strptime(point['date'], '%a')
                    # For longer periods, show month abbreviations
                    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                    # Use a simple mapping for demo - in production, use actual dates
                    month_name = month_names[hash(point['date']) % 12]
                    formatted_point = point.copy()
                    formatted_point['date'] = month_name
                    formatted_points.append(formatted_point)
                except:
                    formatted_points.append(point)
            else:
                formatted_points.append(point)
        formatted_data[key] = formatted_points
    
    return formatted_data

@app.route("/api/wellness-tasks", methods=["GET", "POST"])
def wellness_tasks():
    user_id = session.get('user_id', 'default_user')
    
    # Get or create user
    db.get_or_create_user(user_id)
    
    if request.method == "POST":
        try:
            data = request.get_json()
            task_name = data.get("task_id", "")
            points = data.get("points", 0)
            completed = data.get("completed", True)
            
            # Save task to database
            success = db.save_wellness_task(user_id, task_name, points, completed)
            
            if success:
                # Get updated streak data
                streak_data = db.get_streak_data(user_id)
                return jsonify({
                    "success": True, 
                    "points": points,
                    "streak": streak_data['current_streak'],
                    "completion_rate": streak_data['completion_rate']
                })
            else:
                return jsonify({"error": "Failed to save task"}), 500
                
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        # Get daily tasks from database
        try:
            tasks = db.get_wellness_tasks(user_id)
            return jsonify(tasks)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

@app.route("/api/save-mood", methods=["POST"])
def save_mood():
    try:
        data = request.get_json()
        user_id = session.get('user_id', 'default_user')
        
        # Get or create user
        db.get_or_create_user(user_id)
        
        mood = data.get('mood', '')
        note = data.get('note', '')
        score = 4.0  # Default score, could be calculated based on mood
        
        # Save mood to database
        success = db.save_mood_entry(user_id, mood, score, note)
        
        if success:
            # Get updated streak data
            streak_data = db.get_streak_data(user_id)
            return jsonify({
                "success": True,
                "streak": streak_data['current_streak'],
                "completion_rate": streak_data['completion_rate']
            })
        else:
            return jsonify({"error": "Failed to save mood"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/streak-data")
def get_streak_data():
    try:
        user_id = session.get('user_id', 'default_user')
        
        # Get or create user
        db.get_or_create_user(user_id)
        
        # Get streak data
        streak_data = db.get_streak_data(user_id)
        
        return jsonify(streak_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/quick-stats")
def get_quick_stats():
    try:
        user_id = session.get('user_id')
        if not user_id:
            # Create a session if none exists
            user_id = f"user_{random.randint(10000, 99999)}"
            session['user_id'] = user_id
        
        # Get or create user
        db.get_or_create_user(user_id)
        
        # Get user metrics
        metrics = db.get_dashboard_metrics(user_id)
        streak_data = db.get_streak_data(user_id)
        
        # Get today's completed tasks
        conn = sqlite3.connect("wellness_data.db")
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) as count FROM wellness_tasks 
            WHERE user_id = ? AND completed = 1 AND date = date('now')
        ''', (user_id,))
        
        today_tasks = cursor.fetchone()[0]
        
        cursor.execute('''
            SELECT COUNT(*) as count FROM mood_entries 
            WHERE user_id = ? AND DATE(timestamp) = date('now')
        ''', (user_id,))
        
        today_moods = cursor.fetchone()[0]
        
        conn.close()
        
        quick_stats = {
            "wellbeing_score": f"{metrics['wellbeing_score']}%",
            "current_streak": streak_data['current_streak'],
            "daily_tasks": today_tasks,
            "mood_checkins": today_moods,
            "completion_rate": f"{streak_data['completion_rate']}%",
            "user_id": user_id  # Add for debugging
        }
        
        return jsonify(quick_stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/achievements")
def get_achievements():
    try:
        user_id = session.get('user_id')
        if not user_id:
            # Try to use an existing user that has data
            try:
                conn = sqlite3.connect('wellness_data.db')
                cursor = conn.cursor()
                # Get today's date and find user with activity data
                from datetime import datetime
                today = datetime.now().date()
                cursor.execute('''
                    SELECT user_id FROM streaks 
                    WHERE current_streak > 0
                    ORDER BY current_streak DESC, last_activity_date DESC 
                    LIMIT 1
                ''')
                result = cursor.fetchone()
                conn.close()
                
                if result:
                    user_id = result[0]
                    session['user_id'] = user_id
                    session.permanent = True
                    print(f"Using existing user with streak data: {user_id}")
                else:
                    # Initialize session if no existing data found
                    user_id = f"user_{random.randint(10000, 99999)}"
                    session['user_id'] = user_id
                    session.permanent = True
                    print(f"Created new user: {user_id}")
            except Exception as e:
                print(f"Error getting existing user: {e}")
                user_id = f"user_{random.randint(10000, 99999)}"
                session['user_id'] = user_id
                session.permanent = True
        
        # Get or create user
        db.get_or_create_user(user_id)
        
        # Get streak data
        streak_data = db.get_streak_data(user_id)
        print(f"Debug - User ID: {user_id}")
        print(f"Debug - Streak data: {streak_data}")
        
        # Get mood entries count
        conn = sqlite3.connect("wellness_data.db")
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) as count FROM mood_entries 
            WHERE user_id = ? AND timestamp >= datetime('now', '-7 days')
        ''', (user_id,))
        
        mood_count = cursor.fetchone()[0]
        print(f"Debug - Mood count: {mood_count}")
        
        cursor.execute('''
            SELECT COUNT(*) as count FROM wellness_tasks 
            WHERE user_id = ? AND completed = 1 AND date >= date('now', '-7 days')
        ''', (user_id,))
        
        tasks_completed = cursor.fetchone()[0]
        print(f"Debug - Tasks completed: {tasks_completed}")
        
        conn.close()
        
        achievements = []
        
        # Week Warrior - 7 day streak
        if streak_data['current_streak'] >= 7:
            achievements.append({
                "title": "Week Warrior",
                "description": f"{streak_data['current_streak']}-day streak completed",
                "icon": "fa-fire",
                "date": "Today",
                "unlocked": True
            })
        elif streak_data['current_streak'] >= 1:
            achievements.append({
                "title": "Getting Started",
                "description": f"{streak_data['current_streak']}-day streak",
                "icon": "fa-fire",
                "date": "Today",
                "unlocked": True
            })
        
        # Mood Master - mood check-ins
        if mood_count >= 10:
            achievements.append({
                "title": "Mindful Master",
                "description": f"Completed {mood_count} mood check-ins",
                "icon": "fa-brain",
                "date": "This week",
                "unlocked": True
            })
        elif mood_count >= 5:
            achievements.append({
                "title": "Mood Tracker",
                "description": f"Completed {mood_count} mood check-ins",
                "icon": "fa-brain",
                "date": "This week",
                "unlocked": True
            })
        
        # Task Champion - completed tasks
        if tasks_completed >= 10:
            achievements.append({
                "title": "Task Champion",
                "description": f"Completed {tasks_completed} wellness tasks",
                "icon": "fa-check-circle",
                "date": "This week",
                "unlocked": True
            })
        elif tasks_completed >= 5:
            achievements.append({
                "title": "Task Starter",
                "description": f"Completed {tasks_completed} wellness tasks",
                "icon": "fa-check-circle",
                "date": "This week",
                "unlocked": True
            })
        
        return jsonify(achievements)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/goals")
def get_goals():
    try:
        user_id = session.get('user_id', 'default_user')
        
        # Get or create user
        db.get_or_create_user(user_id)
        
        # Get user metrics
        metrics = db.get_dashboard_metrics(user_id)
        streak_data = db.get_streak_data(user_id)
        
        goals = [
            {
                "title": "Daily Screen Time",
                "current": metrics['daily_screen_time'],
                "target": 4.0,
                "unit": "hours",
                "progress": min(100, (metrics['daily_screen_time'] / 4.0) * 100)
            },
            {
                "title": "Weekly Streak",
                "current": streak_data['current_streak'],
                "target": 7,
                "unit": "days",
                "progress": min(100, (streak_data['current_streak'] / 7) * 100)
            },
            {
                "title": "Wellness Score",
                "current": metrics['wellbeing_score'],
                "target": 85,
                "unit": "%",
                "progress": metrics['wellbeing_score']
            }
        ]
        
        return jsonify(goals)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/insights")
def get_insights():
    try:
        user_id = session.get('user_id', 'default_user')
        
        # Get or create user
        db.get_or_create_user(user_id)
        
        # Get user metrics
        metrics = db.get_dashboard_metrics(user_id)
        streak_data = db.get_streak_data(user_id)
        
        insights = []
        
        # Digital Balance insight
        if metrics['daily_screen_time'] > 5:
            insights.append({
                "title": "Digital Balance",
                "status": "Attention Needed",
                "status_type": "warning",
                "description": f"Your screen time is {metrics['daily_screen_time']} hours. Consider reducing by 30 minutes.",
                "metrics": [
                    {"value": f"{metrics['daily_screen_time']}h", "label": "Daily Usage"},
                    {"value": "High", "label": "Risk Level"}
                ]
            })
        elif metrics['daily_screen_time'] > 3:
            insights.append({
                "title": "Digital Balance",
                "status": "Good",
                "status_type": "positive",
                "description": f"Your screen time is {metrics['daily_screen_time']} hours. You're doing well!",
                "metrics": [
                    {"value": f"{metrics['daily_screen_time']}h", "label": "Daily Usage"},
                    {"value": "Moderate", "label": "Risk Level"}
                ]
            })
        else:
            insights.append({
                "title": "Digital Balance",
                "status": "Excellent",
                "status_type": "positive",
                "description": f"Great job! Your screen time is only {metrics['daily_screen_time']} hours.",
                "metrics": [
                    {"value": f"{metrics['daily_screen_time']}h", "label": "Daily Usage"},
                    {"value": "Low", "label": "Risk Level"}
                ]
            })
        
        # Streak insight
        if streak_data['current_streak'] >= 7:
            insights.append({
                "title": "Consistency Champion",
                "status": "Excellent",
                "status_type": "positive",
                "description": f"Amazing {streak_data['current_streak']}-day streak! Keep it up!",
                "metrics": [
                    {"value": f"{streak_data['current_streak']}", "label": "Current Streak"},
                    {"value": f"{streak_data['completion_rate']}%", "label": "Completion Rate"}
                ]
            })
        elif streak_data['current_streak'] >= 3:
            insights.append({
                "title": "Building Momentum",
                "status": "Good",
                "status_type": "positive",
                "description": f"Nice work! {streak_data['current_streak']}-day streak. Keep going!",
                "metrics": [
                    {"value": f"{streak_data['current_streak']}", "label": "Current Streak"},
                    {"value": f"{streak_data['completion_rate']}%", "label": "Completion Rate"}
                ]
            })
        else:
            insights.append({
                "title": "Getting Started",
                "status": "Needs Attention",
                "status_type": "warning",
                "description": f"Current streak: {streak_data['current_streak']} days. Try to complete daily tasks!",
                "metrics": [
                    {"value": f"{streak_data['current_streak']}", "label": "Current Streak"},
                    {"value": f"{streak_data['completion_rate']}%", "label": "Completion Rate"}
                ]
            })
        
        # Mood insight
        if metrics['avg_mood'] >= 4:
            insights.append({
                "title": "Emotional Wellbeing",
                "status": "Excellent",
                "status_type": "positive",
                "description": f"Your average mood is {metrics['avg_mood']}/5. Keep up the positive mindset!",
                "metrics": [
                    {"value": f"{metrics['avg_mood']}/5", "label": "Mood Score"},
                    {"value": "Positive", "label": "Trend"}
                ]
            })
        else:
            insights.append({
                "title": "Emotional Wellbeing",
                "status": "Needs Attention",
                "status_type": "warning",
                "description": f"Your average mood is {metrics['avg_mood']}/5. Consider mood check-ins.",
                "metrics": [
                    {"value": f"{metrics['avg_mood']}/5", "label": "Mood Score"},
                    {"value": "Check Needed", "label": "Trend"}
                ]
            })
        
        return jsonify(insights)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Helper functions
def calculate_mood_score(data):
    # Simple mood score calculation
    return 4.2

def determine_emotional_state(score):
    if score >= 4.5:
        return "Excellent"
    elif score >= 3.5:
        return "Good"
    elif score >= 2.5:
        return "Balanced"
    else:
        return "Needs Attention"

def assess_risk_level(data):
    return "Low"

def generate_insights(data):
    return [
        "Your digital habits show good balance",
        "Consider taking regular breaks",
        "Your sleep patterns are healthy"
    ]

def generate_recommendations(data):
    return [
        "Try a digital detox before bedtime",
        "Schedule regular face-to-face interactions",
        "Practice mindfulness exercises"
    ]

@app.route("/predict", methods=["POST"])
def predict():
    try:
        # Ensure session exists
        if 'user_id' not in session:
            session['user_id'] = f"user_{random.randint(10000, 99999)}"
            session.permanent = True
        
        # Handle AI-guided form submission
        if request.form.get("source") == "ai_guided":
            # Convert emoji-based responses to numeric values
            daily_screen_time = float(request.form.get("daily_screen_time", 5))
            gaming_time = float(request.form.get("gaming_time", 2))
            social_media_usage = float(request.form.get("social_media_usage", 3))
            app_sessions = float(request.form.get("app_sessions", 50))
            notifications = float(request.form.get("notifications", 100))
            night_usage = float(request.form.get("night_usage", 2))
        else:
            # Traditional form submission
            daily_screen_time = float(request.form["daily_screen_time"])
            gaming_time = float(request.form["gaming_time"])
            social_media_usage = float(request.form["social_media_usage"])
            app_sessions = float(request.form["app_sessions"])
            notifications = float(request.form["notifications"])
            night_usage = float(request.form["night_usage"])

        # Model input
        input_data = np.array([
            daily_screen_time,
            gaming_time,
            social_media_usage,
            app_sessions,
            notifications,
            night_usage
        ]).reshape(1, -1)

        # Debug: Print input data
        print(f"Input data: {input_data}")
        print(f"Input shape: {input_data.shape}")

        # Prediction
        try:
            prediction = model.predict(input_data)[0]
            probability = model.predict_proba(input_data)[0][prediction]
            print(f"Raw prediction: {prediction}")
            print(f"Probability: {probability}")
        except Exception as e:
            print(f"Prediction error: {e}")
            return render_template("ai_guided_home.html", 
                                 prediction_text="Error in prediction", 
                                 confidence=0, 
                                 risk="Unknown")

        confidence = round(probability * 100, 2)

        if prediction == 1:
            result = "User is Digitally Addicted"
        else:
            result = "User is Not Digitally Addicted"

        # Risk level
        if confidence < 40:
            risk = "Low"
        elif confidence < 70:
            risk = "Medium"
        else:
            risk = "High"

        # Store session data for psychological analysis
        session_id = str(random.randint(1000, 9999))
        user_sessions[session_id] = {
            'prediction': prediction,
            'confidence': confidence,
            'risk': risk,
            'usage_data': {
                'daily_screen_time': daily_screen_time,
                'gaming_time': gaming_time,
                'social_media_usage': social_media_usage,
                'app_sessions': app_sessions,
                'notifications': notifications,
                'night_usage': night_usage
            },
            'timestamp': datetime.now()
        }
        
        # Save screen time data to database for ongoing tracking
        user_id = session.get('user_id')
        try:
            db.get_or_create_user(user_id)
            db.save_screen_time(user_id, daily_screen_time, int(app_sessions), int(notifications), night_usage)
            print(f"Screen time saved for user {user_id}: {daily_screen_time} hours")
        except Exception as e:
            print(f"Error saving screen time: {e}")
            # Continue without saving screen time if there's an error

        return render_template(
            "ai_guided_home.html",
            prediction_text=result,
            confidence=confidence,
            risk=risk,
            session_id=session_id
        )

    except ValueError:
        return render_template(
            "ai_guided_home.html",
            prediction_text="Invalid input. Please enter valid numbers."
        )

@app.route("/analyze-mood", methods=["POST"])
def analyze_mood():
    try:
        # Get mood responses
        responses = [
            request.form.get("anxiety_without_phone"),
            request.form.get("loneliness_after_social"),
            request.form.get("mood_impact"),
            request.form.get("stress_after_usage"),
            request.form.get("concentration_level")
        ]
        
        session_id = request.form.get("session_id", "default")
        
        # Analyze mood
        analysis = psych_analyzer.analyze_mood_responses(responses)
        
        if analysis:
            # Get personalized tips and suggestions
            tips = psych_analyzer.get_personalized_tips(analysis)
            suggestions = psych_analyzer.get_interaction_suggestions(analysis)
            
            # Store in session
            if session_id in user_sessions:
                user_sessions[session_id]['mood_analysis'] = analysis
                user_sessions[session_id]['tips'] = tips
                user_sessions[session_id]['suggestions'] = suggestions
            
            return render_template(
                "mood_analysis.html",
                analysis=analysis,
                tips=tips,
                suggestions=suggestions,
                session_id=session_id
            )
        else:
            return render_template(
                "mood_analysis.html",
                error="Invalid responses. Please ensure all fields are filled correctly."
            )
            
    except Exception as e:
        return render_template(
            "mood_analysis.html",
            error=f"An error occurred: {str(e)}"
        )

@app.route("/detox-plans")
def detox_plans():
    plans = psych_analyzer.generate_digital_detox_plans()
    return render_template("detox_plans.html", plans=plans)

def generate_mock_data(days, min_val, max_val):
    """Generate mock data for visualization"""
    data = []
    for i in range(days):
        data.append({
            "date": (datetime.now() - timedelta(days=days-i-1)).strftime("%Y-%m-%d"),
            "value": random.uniform(min_val, max_val)
        })
    return data

if __name__ == "__main__":
    app.run(debug=True)
