from flask import Flask
from flask import request
from flask import jsonify

from flask_cors import CORS

from rag_engine import review_code

app = Flask(__name__)
CORS(app)

@app.route("/review", methods=["POST"])
def review():

    data = request.json

    code = data["code"]

    result = review_code(code)

    return jsonify(
        {
            "review": result
        }
    )

if __name__ == "__main__":
    app.run(
        debug=True
    )