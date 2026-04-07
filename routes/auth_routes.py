from datetime import datetime, timedelta, timezone

from flask import Blueprint, current_app, jsonify, redirect, render_template, request, session, url_for
import jwt

from database import db
from utils.auth import token_required

auth_bp = Blueprint("auth", __name__)


def create_token(user_id, email, expires_in=86400 * 7):
    expires = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": expires,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, current_app.secret_key, algorithm="HS256")


def set_session_user(user):
    session["user_id"] = user["user_id"]
    session["username"] = user.get("username", "")
    session["email"] = user.get("email", "")
    session["profile_photo"] = user.get("profile_photo", "")
    session.permanent = True
    db.update_last_active(user["user_id"])


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        identifier = request.form.get("username")
        password = request.form.get("password")
        user = db.authenticate_user(identifier, password)
        if not user:
            return render_template("login.html", error="Invalid username, email, or password")
        set_session_user(user)
        return redirect(url_for("pages.home"))
    return render_template("login.html")


@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if not username or not email or not password or not confirm_password:
            return render_template("signup.html", error="All fields are required")
        if password != confirm_password:
            return render_template("signup.html", error="Passwords do not match")
        if len(password) < 6:
            return render_template("signup.html", error="Password must be at least 6 characters")
        if not db.create_user(username, email, password):
            return render_template("signup.html", error="Username or email already exists")

        user = db.authenticate_user(email, password)
        if not user:
            return render_template("signup.html", error="Account created but login failed. Please sign in.")

        db.get_or_create_user(user["user_id"])
        set_session_user(user)
        return redirect(url_for("pages.home"))

    return render_template("signup.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))


@auth_bp.route("/api/auth/register", methods=["POST"])
def api_register():
    data = request.get_json() or {}
    username = data.get("name") or data.get("username", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "").strip()

    if not all([username, email, password]):
        return jsonify({"error": "All fields are required"}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400
    if not db.create_user(username, email, password):
        return jsonify({"error": "Email already exists. Please use a different email or login."}), 409

    user = db.authenticate_user(email, password)
    db.get_or_create_user(user["user_id"])
    set_session_user(user)
    token = create_token(user["user_id"], user["email"])
    response = jsonify(
        {
            "token": token,
            "user": {
                "id": user["user_id"],
                "email": user["email"],
                "name": user.get("username", ""),
                "createdAt": datetime.now().isoformat(),
            },
        }
    )
    response.set_cookie("auth_token", token, httponly=True, secure=True, samesite="Lax")
    return response, 201


@auth_bp.route("/api/auth/login", methods=["POST"])
def api_login():
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "").strip()
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user = db.authenticate_user(email, password)
    if not user:
        return jsonify({"error": "Invalid email or password"}), 401

    set_session_user(user)
    token = create_token(user["user_id"], user["email"])
    response = jsonify(
        {
            "token": token,
            "user": {
                "id": user["user_id"],
                "email": user["email"],
                "name": user.get("username", ""),
            },
        }
    )
    response.set_cookie("auth_token", token, httponly=True, secure=True, samesite="Lax")
    return response, 200


@auth_bp.route("/api/auth/logout", methods=["POST"])
def api_logout():
    session.clear()
    response = jsonify({"success": True})
    response.set_cookie("auth_token", "", expires=0)
    return response, 200


@auth_bp.route("/api/auth/me", methods=["GET"])
@token_required
def api_me():
    user = db.get_user_by_id(request.user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(
        {
            "id": user["user_id"],
            "email": user["email"],
            "name": user.get("username", ""),
            "authProvider": user.get("auth_provider"),
            "createdAt": user.get("created_at"),
        }
    )
