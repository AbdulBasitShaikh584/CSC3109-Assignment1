import datetime
from functools import wraps

import jwt
from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
SECRET_KEY = "change-me-in-production-please-use-a-long-random-secret"  # use an env var in real systems

USERS = {
    "alice": {"password": generate_password_hash("admin123"), "role": "admin"},
    "bob": {"password": generate_password_hash("emp123"), "role": "employee"},
}

EMPLOYEES = {
    1: {"id": 1, "name": "Ahmed Khan", "position": "Developer", "salary": 80000},
    2: {"id": 2, "name": "Sara Ali", "position": "Designer", "salary": 70000},
}
next_id = 3


# ---------- Authentication ----------
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    user = USERS.get(data.get("username"))
    if not user or not check_password_hash(user["password"], data.get("password", "")):
        return jsonify({"error": "Invalid credentials"}), 401
    token = jwt.encode(
        {"sub": data["username"], "role": user["role"],
         "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)},
        SECRET_KEY, algorithm="HS256",
    )
    return jsonify({"token": token})


def login_required(roles=None):
    """401 = not authenticated, 403 = authenticated but not authorized."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            auth = request.headers.get("Authorization", "")
            if not auth.startswith("Bearer "):
                return jsonify({"error": "Authentication required"}), 401
            try:
                payload = jwt.decode(auth[7:], SECRET_KEY, algorithms=["HS256"])
            except jwt.PyJWTError:
                return jsonify({"error": "Invalid or expired token"}), 401
            if roles and payload["role"] not in roles:
                return jsonify({"error": "Forbidden: admin role required"}), 403
            request.user = payload
            return fn(*args, **kwargs)
        return wrapper
    return decorator


# ---------- Employee endpoints ----------
@app.route("/employees", methods=["GET"])
@login_required()
def list_employees():
    return jsonify(list(EMPLOYEES.values()))


@app.route("/employees/<int:eid>", methods=["GET"])
@login_required()
def get_employee(eid):
    emp = EMPLOYEES.get(eid)
    return (jsonify(emp), 200) if emp else (jsonify({"error": "Not found"}), 404)


@app.route("/employees", methods=["POST"])
@login_required(roles=["admin"])
def add_employee():
    global next_id
    data = request.get_json(silent=True) or {}
    if not all(k in data for k in ("name", "position", "salary")):
        return jsonify({"error": "name, position, salary required"}), 400
    EMPLOYEES[next_id] = {"id": next_id, "name": data["name"], "position": data["position"], "salary": data["salary"]}
    next_id += 1
    return jsonify(EMPLOYEES[next_id - 1]), 201


@app.route("/employees/<int:eid>", methods=["PUT"])
@login_required(roles=["admin"])
def update_employee(eid):
    if eid not in EMPLOYEES:
        return jsonify({"error": "Not found"}), 404
    data = request.get_json(silent=True) or {}
    EMPLOYEES[eid].update({k: v for k, v in data.items() if k in ("name", "position", "salary")})
    return jsonify(EMPLOYEES[eid])


@app.route("/employees/<int:eid>", methods=["DELETE"])
@login_required(roles=["admin"])
def delete_employee(eid):
    if EMPLOYEES.pop(eid, None) is None:
        return jsonify({"error": "Not found"}), 404
    return jsonify({"message": "Deleted"})


if __name__ == "__main__":
    app.run(host="localhost", port=5002, debug=True)
