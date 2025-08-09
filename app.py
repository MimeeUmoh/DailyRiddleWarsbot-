from flask import Flask, request
import json
import os
from datetime import datetime

app = Flask(__name__)
users_file = "data/users.json"
riddles_file = "data/riddles.json"
scores_file = "data/scores.json"

# Load and save helpers
def load_users():
    if not os.path.exists(users_file):
        return {}
    with open(users_file, "r") as f:
        return json.load(f)

def save_users(users):
    with open(users_file, "w") as f:
        json.dump(users, f)

def load_riddles():
    with open(riddles_file, "r") as f:
        return json.load(f) 

def load_scores():
    if not os.path.exists(scores_file):
        return {}
    with open(scores_file, "r") as f:
        return json.load(f)

def save_scores(scores):
    with open(scores_file, "w") as f:
        json.dump(scores, f)

# Register new user
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    user_id = str(data["user_id"])
    name = data["name"]
    phone = data["phone"]
    account_number = data["account_number"]
    bank = data["bank"]
    ref = data.get("referrer_id")

    users = load_users()

    if user_id not in users:
        users[user_id] = {
            "name": name,
            "phone": phone,
            "account_number": account_number,
            "bank": bank,
            "coins": 0,
            "is_vip": False,
            "is_premium": False,
            "riddles_solved": [],
            "score": 0,
            "last_login": "",
            "streak": 0,
            "has_paid": False,
            "referrer": ref
        }
        save_users(users)
        return {"status": "registered"}
    return {"status": "already_registered"}

# Mark user as VIP or Premium
@app.route("/mark_paid", methods=["POST"])
def mark_paid():
    data = request.json
    user_id = str(data["user_id"])
    level = data["level"]  # "vip" or "premium"

    users = load_users()
    if user_id in users:
        if level == "vip":
            users[user_id]["is_vip"] = True
        elif level == "premium":
            users[user_id]["is_premium"] = True
        users[user_id]["has_paid"] = True
        save_users(users)
        return {"status": "success"}
    return {"status": "user_not_found"}

# Submit riddle answer
@app.route("/submit_answer", methods=["POST"])
def submit_answer():
    data = request.json
    user_id = str(data["user_id"])
    riddle_id = str(data["riddle_id"])
    answer = data["answer"]
    used_hint = data["used_hint"]

    riddles = load_riddles()
    users = load_users()
    scores = load_scores()

    if user_id not in users:
        return {"error": "User not registered"}

    riddle = riddles.get(riddle_id)
    if not riddle:
        return {"error": "Riddle not found"}

    user = users[user_id]
    if riddle_id in user["riddles_solved"]:
        return {"error": "Riddle already solved"}

    correct = riddle["answer"].lower() == answer.lower()
    score = 10 if correct and not used_hint else 7 if correct else 0

    if correct:
        user["score"] += score
        user["riddles_solved"].append(riddle_id)

        today = datetime.now().strftime("%Y-%m-%d")
        if today not in scores:
            scores[today] = {}
        if user_id not in scores[today]:
            scores[today][user_id] = 0
        scores[today][user_id] += score

        save_scores(scores)

    save_users(users)
    return {"correct": correct, "score": score}

# Get user data
@app.route("/get_user", methods=["GET"])
def get_user():
    user_id = request.args.get("user_id")
    users = load_users()
    if user_id in users:
        return users[user_id]
    return {"error": "User not found"}

# Add coins (buying or reward)
@app.route("/add_coins", methods=["POST"])
def add_coins():
    data = request.json
    user_id = str(data["user_id"])
    coins = int(data["coins"])
    users = load_users()
    if user_id in users:
        users[user_id]["coins"] += coins
        save_users(users)
        return {"status": "coins_added"}
    return {"error": "user_not_found"}

# Use coins for hint
@app.route("/use_hint", methods=["POST"])
def use_hint():
    data = request.json
    user_id = str(data["user_id"])
    users = load_users()
    if user_id in users:
        if users[user_id]["coins"] >= 10:
            users[user_id]["coins"] -= 10
            save_users(users)
            return {"status": "hint_used"}
        else:
            return {"error": "not_enough_coins"}
    return {"error": "user_not_found"}

@app.route("/")
def index():
    return "Daily Riddle Wars Bot is Live!"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

