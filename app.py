from flask import Flask, render_template, request, redirect, session, jsonify
import json
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

USER_DATA_FILE = "users.json"
SCORES_FILE = "scores.json"

# Sample quiz questions
quiz_questions = [
    {"question": "What is the capital of France?", "options": ["Berlin", "Madrid", "Paris", "Rome"], "answer": "Paris"},
    {"question": "Which programming language is known as the backbone of web development?", "options": ["Python", "JavaScript", "C++", "Ruby"], "answer": "JavaScript"},
    {"question": "Who developed the theory of relativity?", "options": ["Isaac Newton", "Albert Einstein", "Galileo Galilei", "Nikola Tesla"], "answer": "Albert Einstein"},
    {"question": "What is the largest planet in our solar system?", "options": ["Earth", "Mars", "Jupiter", "Saturn"], "answer": "Jupiter"}
]

# Load user data
def load_users():
    if not os.path.exists(USER_DATA_FILE):
        return {}
    with open(USER_DATA_FILE, "r") as file:
        return json.load(file)

# Save user data
def save_users(users):
    with open(USER_DATA_FILE, "w") as file:
        json.dump(users, file, indent=4)

# Register route
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    users = load_users()
    
    if data["username"] in users:
        return jsonify({"status": "error", "message": "Username already exists!"}), 400

    users[data["username"]] = data["password"]
    save_users(users)
    return jsonify({"status": "success", "message": "Registration successful!"})

# Login route (Supports both GET and POST)
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = request.json
        users = load_users()

        if data["username"] in users and users[data["username"]] == data["password"]:
            session["user"] = data["username"]
            return jsonify({"status": "success", "message": "Login successful!"})
        
        return jsonify({"status": "error", "message": "Invalid username or password!"}), 400
    
    # Render login page for GET requests
    return render_template("login.html")

# Logout route
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")

# Serve the quiz page
@app.route("/")
def quiz():
    if "user" not in session:
        return redirect("/login")
    return render_template("quiz.html", questions=quiz_questions, username=session["user"])

# Score submission route
@app.route("/submit_score", methods=["POST"])
def submit_score():
    if "user" not in session:
        return jsonify({"status": "error", "message": "User not logged in!"}), 403

    data = request.json
    username = session["user"]
    
    # Load existing scores
    scores = {}
    if os.path.exists(SCORES_FILE):
        with open(SCORES_FILE, "r") as file:
            scores = json.load(file)

    # Save new score
    scores[username] = data["score"]
    with open(SCORES_FILE, "w") as file:
        json.dump(scores, file, indent=4)

    return jsonify({"status": "success", "message": "Score saved successfully!"})

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
