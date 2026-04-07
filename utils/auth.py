from functools import wraps

from flask import current_app, jsonify, redirect, request, session, url_for
import jwt


def get_request_user_id():
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1]
        try:
            decoded = jwt.decode(token, current_app.secret_key, algorithms=["HS256"])
            request.user_id = decoded["user_id"]
            request.email = decoded.get("email")
            return decoded["user_id"]
        except jwt.InvalidTokenError:
            return None
    user_id = session.get("user_id")
    if user_id:
        request.user_id = user_id
        request.email = session.get("email")
    return user_id


def login_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return view_func(*args, **kwargs)

    return wrapped


def token_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not get_request_user_id():
            return jsonify({"error": "Unauthorized"}), 401
        return view_func(*args, **kwargs)

    return wrapped
