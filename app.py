"""
app.py
======
Flask backend web server for the FAQ Chatbot.

Routes:
- GET  /     : Renders the chat user interface (index.html).
- POST /ask  : Receives a JSON payload {"question": "..."}, runs it
               through the chatbot engine, and returns matching answer,
               matched question, and similarity confidence score.
"""

from flask import Flask, render_template, request, jsonify
from chatbot import get_chatbot_response

# Initialize Flask application
app = Flask(__name__)


@app.route("/")
def index():
    """
    Renders the main chat application homepage.
    """
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask():
    """
    API endpoint to handle incoming chat questions from the user.
    
    Expected JSON Request:
        { "question": "How can I track my order?" }
        
    JSON Response:
        {
            "answer": "...",
            "matched_question": "...",
            "confidence": 0.82
        }
    """
    try:
        # Check if request has JSON payload
        data = request.get_json(silent=True)
        if not data or not isinstance(data, dict):
            return jsonify({
                "error": "Invalid request format. Expected JSON payload with 'question' field.",
                "answer": "Please provide a valid question format.",
                "matched_question": None,
                "confidence": 0.0
            }), 400

        # Extract and clean user question
        user_question = data.get("question", "").strip()

        # Handle empty question submission
        if not user_question:
            return jsonify({
                "error": "Question cannot be empty.",
                "answer": "Please type a question before sending!",
                "matched_question": None,
                "confidence": 0.0
            }), 400

        # Query the chatbot NLP engine
        result = get_chatbot_response(user_question)

        # Return successful response
        return jsonify(result), 200

    except Exception as e:
        # Graceful error handling for unexpected exceptions
        print(f"[Error in /ask route]: {e}")
        return jsonify({
            "error": "An internal server error occurred while processing your request.",
            "answer": "Sorry, something went wrong on our end. Please try again shortly.",
            "matched_question": None,
            "confidence": 0.0
        }), 500


if __name__ == "__main__":
    # Run Flask local development server
    # debug=True allows hot-reloading during development
    app.run(host="127.0.0.1", port=5000, debug=True)
