from flask import Flask, request, jsonify
from qa2 import ask_ai_ta
from flask_cors import cross_origin

from flask_cors import CORS


app = Flask(__name__)
CORS(app, origins=["http://localhost:5173", "http://127.0.0.1:5173"])


@app.route("/ask", methods=["POST"])
@cross_origin(origins=["http://localhost:5173"])
def ask():
    data = request.get_json()
    question = data.get("question", "")
    course = data.get("course")

    if not question:
        return jsonify({"error": "Question is required"}), 400

    answer = ask_ai_ta(question, course=course)
    return jsonify({"answer": answer})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
