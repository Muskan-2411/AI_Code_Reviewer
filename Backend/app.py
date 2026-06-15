import os
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, jsonify
from flask_cors import CORS
from rag_engine import review_code

app = Flask(__name__)

# ------------------------------------
# CORS Configuration for Railway
# ------------------------------------
# Allow the deployed frontend URL + localhost for development
frontend_url = os.environ.get("FRONTEND_URL", "")
allowed_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
if frontend_url:
    # Strip trailing slash and add the origin
    allowed_origins.append(frontend_url.rstrip("/"))

CORS(app, origins=allowed_origins, supports_credentials=True)


# ------------------------------------
# Health Check — Railway uses this
# ------------------------------------
@app.route("/", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "service": "AI Code Reviewer API",
        "version": "1.0.0"
    })


# ------------------------------------
# Code Review Endpoint
# ------------------------------------
@app.route("/review", methods=["POST"])
def review():
    data = request.get_json(silent=True)

    if not data or "code" not in data:
        return jsonify({"error": "Missing 'code' field in request body"}), 400

    code = data["code"].strip()
    if not code:
        return jsonify({"error": "Code cannot be empty"}), 400

    result = review_code(code)

    return jsonify({"review": result})


# ------------------------------------
# Error Handlers
# ------------------------------------
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error"}), 500


# ------------------------------------
# Entry Point
# ------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)