import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)
DB = "students.db"


def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS students (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   name TEXT NOT NULL,
                   department TEXT NOT NULL,
                   email TEXT NOT NULL UNIQUE
               )"""
        )


def validate(data):
    return data and all(str(data.get(k, "")).strip() for k in ("name", "department", "email"))


@app.route("/students", methods=["GET"])
def get_students():
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM students").fetchall()
    return jsonify([dict(r) for r in rows])


@app.route("/students/<int:sid>", methods=["GET"])
def get_student(sid):
    with get_db() as conn:
        row = conn.execute("SELECT * FROM students WHERE id = ?", (sid,)).fetchone()
    if row is None:
        return jsonify({"error": "Student not found"}), 404
    return jsonify(dict(row))


@app.route("/students", methods=["POST"])
def add_student():
    data = request.get_json(silent=True)
    if not validate(data):
        return jsonify({"error": "name, department and email are required"}), 400
    try:
        with get_db() as conn:
            cur = conn.execute(
                "INSERT INTO students (name, department, email) VALUES (?, ?, ?)",
                (data["name"], data["department"], data["email"]),
            )
            new_id = cur.lastrowid
    except sqlite3.IntegrityError:
        return jsonify({"error": "Email already exists"}), 409
    return jsonify({"message": "Student added", "id": new_id}), 201


@app.route("/students/<int:sid>", methods=["PUT"])
def update_student(sid):
    data = request.get_json(silent=True)
    if not validate(data):
        return jsonify({"error": "name, department and email are required"}), 400
    try:
        with get_db() as conn:
            cur = conn.execute(
                "UPDATE students SET name=?, department=?, email=? WHERE id=?",
                (data["name"], data["department"], data["email"], sid),
            )
    except sqlite3.IntegrityError:
        return jsonify({"error": "Email already exists"}), 409
    if cur.rowcount == 0:
        return jsonify({"error": "Student not found"}), 404
    return jsonify({"message": "Student updated"})


@app.route("/students/<int:sid>", methods=["DELETE"])
def delete_student(sid):
    with get_db() as conn:
        cur = conn.execute("DELETE FROM students WHERE id = ?", (sid,))
    if cur.rowcount == 0:
        return jsonify({"error": "Student not found"}), 404
    return jsonify({"message": "Student deleted"})


if __name__ == "__main__":
    init_db()
    app.run(host="localhost", port=5000, debug=True)
