import hashlib, json
from functools import wraps
from flask import Flask, request, jsonify

app = Flask(__name__)

try:
    with open("keys.json") as f:
        KEY_HASHES = json.load(f)  # {sha256(key): consumer_name}
except FileNotFoundError:
    KEY_HASHES = {}
    print("keys.json not found - run generate_keys.py first")


def require_api_key(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        key = request.headers.get("X-API-Key")
        if not key:
            return jsonify({"error": "Missing API key"}), 401
        consumer = KEY_HASHES.get(hashlib.sha256(key.encode()).hexdigest())
        if consumer is None:
            return jsonify({"error": "Invalid API key"}), 403
        request.consumer = consumer
        return fn(*args, **kwargs)
    return wrapper


@app.route("/process", methods=["POST"])
@require_api_key
def process():
    data = request.get_json(silent=True)
    if not data or not isinstance(data.get("text"), str):
        return jsonify({"error": "JSON body with a 'text' string is required"}), 400
    return jsonify({"consumer": request.consumer, "original": data["text"], "processed": data["text"].upper()})


if __name__ == "__main__":
    app.run(host="localhost", port=5001, debug=True)
