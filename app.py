import os
import json
import requests
from datetime import datetime
from flask import Flask, request

app = Flask(__name__)

# Data file paths
DATA_DIR = "data"
users_file = os.path.join(DATA_DIR, "users.json")
riddles_file = os.path.join(DATA_DIR, "riddles.json")
scores_file = os.path.join(DATA_DIR, "scores.json")
user_states_file = os.path.join(DATA_DIR, "user_states.json")

BOT_TOKEN = os.environ.get("BOT_TOKEN")  # Set your Telegram bot token as env variable

# Ensure data directory and files exist, create empty JSON if missing
def ensure_file(file_path):
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            f.write("{}")

for file in [users_file, riddles_file, scores_file, user_states_file]:
    ensure_file(file)

def load_json(file_path):
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return {}

def save_json(data, file_path):
    try:
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error saving {file_path}: {e}")

def load_users():
    return load_json(users_file)

def save_users(users):
    save_json(users, users_file)

def load_riddles():
    return load_json(riddles_file)

def load_scores():
    return load_json(scores_file)

def save_scores(scores):
    save_json(scores, scores_file)

def load_user_states():
    return load_json(user_states_file)

def save_user_states(states):
    save_json(states, user_states_file)

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    try:
        response = requests.post(url, json=payload)
        if not response.ok:
            print(f"Failed to send message: {response.text}")
    except Exception as e:
        print(f"Exception sending message: {e}")

def get_next_riddle_question(user_id, users, riddles):
    user = users[user_id]
    unsolved = [rid for rid in riddles if rid not in user["riddles_solved"]]
    if unsolved:
        return riddles[unsolved[0]]["question"]
    else:
        return "You have completed all riddles! 🎉"

def check_riddle_answer(user_id, answer, users, riddles, scores):
    if user_id not in users:
        return {"error": "User not registered"}

    user = users[user_id]
    unsolved = [rid for rid in riddles if rid not in user["riddles_solved"]]

    if not unsolved:
        return {"message": "You have solved all available riddles!"}

    riddle_id = unsolved[0]
    riddle = riddles[riddle_id]

    correct = riddle["answer"].strip().lower() == answer.strip().lower()
    score = 10 if correct else 0

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
        return {"correct": True, "score": user["score"], "riddle": riddle["question"]}
    else:
        return {"correct": False, "riddle": riddle["question"]}

@app.route("/webhook", methods=["POST"])
def telegram_webhook():
    update = request.get_json()
    if not update or "message" not in update:
        return "ok"

    message = update["message"]
    chat_id = message["chat"]["id"]
    user_id = str(message["from"]["id"])
    text = message.get("text", "").strip()

    users = load_users()
    riddles = load_riddles()
    scores = load_scores()
    user_states = load_user_states()

    # Registration flow
    if user_id in user_states:
        state = user_states[user_id].get("state")

        if state == "awaiting_name":
            user_states[user_id]["name"] = text
            user_states[user_id]["state"] = "awaiting_phone"
            save_user_states(user_states)
            send_message(chat_id, "Please enter your phone number:")
            return "ok"

        if state == "awaiting_phone":
            user_states[user_id]["phone"] = text
            user_states[user_id]["state"] = "awaiting_account"
            save_user_states(user_states)
            send_message(chat_id, "Please enter your bank account number:")
            return "ok"

        if state == "awaiting_account":
            user_states[user_id]["account_number"] = text
            user_states[user_id]["state"] = "awaiting_bank"
            save_user_states(user_states)
            send_message(chat_id, "Please enter your bank name:")
            return "ok"

        if state == "awaiting_bank":
            user_states[user_id]["bank"] = text
            # Save user
            users[user_id] = {
                "name": user_states[user_id]["name"],
                "phone": user_states[user_id]["phone"],
                "account_number": user_states[user_id]["account_number"],
                "bank": user_states[user_id]["bank"],
                "coins": 0,
                "is_vip": False,
                "is_premium": False,
                "riddles_solved": [],
                "score": 0,
                "last_login": "",
                "streak": 0,
                "has_paid": False,
                "referrer": None
            }
            save_users(users)
            user_states.pop(user_id)
            save_user_states(user_states)
            send_message(chat_id, "Registration complete! You can now play Daily Riddle Wars.")
            first_riddle = get_next_riddle_question(user_id, users, riddles)
            send_message(chat_id, f"Here is your first riddle:\n{first_riddle}")
            return "ok"

    # Handle commands
    if text == "/start":
        send_message(chat_id, "Welcome to Daily Riddle Wars Bot! Use /register to get started.")
        return "ok"

    if text == "/help":
        send_message(chat_id,
            "Commands:\n"
            "/start - Welcome message\n"
            "/help - This message\n"
            "/register - Register to start playing\n"
            "/coins - Show your coins\n"
            "/buycoins [amount] - Add coins (demo)\n"
            "/hint - Use 10 coins for a hint\n"
            "/leaderboard - Show today's top players\n"
            "/profile - Show your stats\n"
            "After registration, send answers as messages to solve riddles."
        )
        return "ok"

    if text == "/register":
        if user_id in users:
            send_message(chat_id, "You are already registered!")
        else:
            user_states[user_id] = {"state": "awaiting_name"}
            save_user_states(user_states)
            send_message(chat_id, "Please enter your full name:")
        return "ok"

    if text == "/coins":
        if user_id in users:
            coins = users[user_id]["coins"]
            send_message(chat_id, f"You have {coins} coins.")
        else:
            send_message(chat_id, "Please register first using /register.")
        return "ok"

    if text.startswith("/buycoins"):
        if user_id in users:
            try:
                amount = int(text.split()[1])
                users[user_id]["coins"] += amount
                save_users(users)
                send_message(chat_id, f"Added {amount} coins to your balance.")
            except:
                send_message(chat_id, "Usage: /buycoins 50")
        else:
            send_message(chat_id, "Please register first using /register.")
        return "ok"

    if text == "/hint":
        if user_id in users:
            if users[user_id]["coins"] >= 10:
                users[user_id]["coins"] -= 10
                save_users(users)
                unsolved = [rid for rid in riddles if rid not in users[user_id]["riddles_solved"]]
                if unsolved:
                    hint = riddles[unsolved[0]]["answer"][:3] + "..."
                    send_message(chat_id, f"Hint: {hint}")
                else:
                    send_message(chat_id, "No more riddles left!")
            else:
                send_message(chat_id, "You don’t have enough coins for a hint.")
        else:
            send_message(chat_id, "Please register first using /register.")
        return "ok"

    if text == "/leaderboard":
        today = datetime.now().strftime("%Y-%m-%d")
        today_scores = scores.get(today, {})
        if not today_scores:
            send_message(chat_id, "No scores recorded for today yet.")
        else:
            sorted_scores = sorted(today_scores.items(), key=lambda x: x[1], reverse=True)[:5]
            leaderboard_text = "Today's Leaderboard:\n"
            for rank, (uid, score) in enumerate(sorted_scores, start=1):
                name = users.get(uid, {}).get("name", "Unknown")
                leaderboard_text += f"{rank}. {name} - {score} pts\n"
            send_message(chat_id, leaderboard_text)
        return "ok"

    if text == "/profile":
        if user_id in users:
            user = users[user_id]
            profile_text = (
                f"Name: {user['name']}\n"
                f"Score: {user['score']}\n"
                f"Coins: {user['coins']}\n"
                f"Riddles solved: {len(user['riddles_solved'])}\n"
                f"VIP: {'Yes' if user['is_vip'] else 'No'}\n"
                f"Premium: {'Yes' if user['is_premium'] else 'No'}"
            )
            send_message(chat_id, profile_text)
        else:
            send_message(chat_id, "Please register first using /register.")
        return "ok"

    # Handle riddle answers
    if user_id in users:
        if text.startswith("/"):
            send_message(chat_id, "Unknown command. Use /help for commands.")
        else:
            result = check_riddle_answer(user_id, text, users, riddles, scores)
            if "error" in result:
                send_message(chat_id, result["error"])
            elif "message" in result:
                send_message(chat_id, result["message"])
            elif result["correct"]:
                next_riddle = get_next_riddle_question(user_id, users, riddles)
                send_message(chat_id, f"Correct! 🎉 Your score is now {result['score']}.\nNext riddle:\n{next_riddle}")
            else:
                send_message(chat_id, f"Wrong answer. Try again!\nRiddle:\n{result['riddle']}")
        return "ok"

    send_message(chat_id, "Please register first using /register")
    return "ok"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
