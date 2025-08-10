import os
import json
import logging
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
import requests
import hmac
import hashlib
import uuid

app = Flask(__name__)

# --------------------
# Config & Globals
# --------------------

DATA_DIR = "data"
USERS_FILE = os.path.join(DATA_DIR, "users.json")
SCORES_FILE = os.path.join(DATA_DIR, "scores.json")
RIDDLES_DIR = os.path.join(DATA_DIR, "riddles")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

PAYSTACK_SECRET_KEY = os.getenv("PAYSTACK_SECRET_KEY")
PAYSTACK_BASE_URL = "https://api.paystack.co"

MONETAG_KEY = os.getenv("MONETAG_KEY")

ENTRY_FEES = {
    "free": 0,
    "vip": 2000,
    "premium": 500,
}

UNLOCK_ALL_FEES = {
    "vip": 200,
    "premium": 100,
}

PRIZES = {
    "vip": {
        "1": 10000,
        "2": 5000,
        "3": 3000,
        "4-10": 1000,  # airtime
    },
    "premium": {
        "1": 5000,
        "2": 3000,
        "3": 1000,
        "4-10": 500,  # airtime
    },
    "free": {
        "no_cash_prize": True,
    },
}

COIN_PACKS = {
    50: 200,
    100: 350,
    200: 600,
    500: 1200,
}

HINT_COST = 10
POINTS_CORRECT_ANSWER = 10
POINTS_HINT_PENALTY = 3

MAX_DAILY_RIDDLES = 7
SATURDAY_RIDDLES_COUNT = 10

logging.basicConfig(level=logging.INFO)

# --------------------
# Utility Functions
# --------------------

def load_json(filename):
    if not os.path.exists(filename):
        return {}
    with open(filename, "r") as f:
        return json.load(f)

def save_json(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

def send_message(chat_id, text, reply_markup=None):
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
    }
    if reply_markup:
        data["reply_markup"] = json.dumps(reply_markup)
    requests.post(f"{TELEGRAM_API_URL}/sendMessage", data=data)

def edit_message(chat_id, message_id, text, reply_markup=None):
    data = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text,
        "parse_mode": "Markdown",
    }
    if reply_markup:
        data["reply_markup"] = json.dumps(reply_markup)
    requests.post(f"{TELEGRAM_API_URL}/editMessageText", data=data)

def get_user_data(user_id):
    users = load_json(USERS_FILE)
    return users.get(str(user_id))

def update_user_data(user_id, user_data):
    users = load_json(USERS_FILE)
    users[str(user_id)] = user_data
    save_json(USERS_FILE, users)

def get_scores():
    return load_json(SCORES_FILE)

def update_scores(scores):
    save_json(SCORES_FILE, scores)

def get_riddles(section):
    riddles_file = os.path.join(RIDDLES_DIR, f"{section}.json")
    return load_json(riddles_file)

def verify_paystack_signature(request):
    signature = request.headers.get('X-Paystack-Signature')
    body = request.get_data()
    computed_signature = hmac.new(
        PAYSTACK_SECRET_KEY.encode('utf-8'),
        body,
        hashlib.sha512
    ).hexdigest()
    return hmac.compare_digest(computed_signature, signature)

def generate_paystack_payment_link(email, amount, reference, metadata):
    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "email": email,
        "amount": amount,
        "reference": reference,
        "metadata": metadata,
        "callback_url": os.getenv("PAYSTACK_CALLBACK_URL"),
    }
    response = requests.post(f"{PAYSTACK_BASE_URL}/transaction/initialize", json=data, headers=headers)
    res_json = response.json()
    if res_json.get("status") and res_json.get("data"):
        return res_json["data"]["authorization_url"], res_json["data"]["reference"]
    return None, None

def format_leaderboard_text(scores, section):
    if not scores or section not in scores:
        return "No scores yet."
    sorted_scores = sorted(scores[section].items(), key=lambda x: x[1]["points"], reverse=True)
    text = f"*Leaderboard for {section.capitalize()} Section:*\n\n"
    for i, (user_id, data) in enumerate(sorted_scores[:10], 1):
        username = data.get("username", "Anonymous")
        points = data.get("points", 0)
        text += f"{i}. {username}: {points} points\n"
    return text

def reset_daily_data_if_needed(user_data):
    today_str = datetime.utcnow().strftime("%Y-%m-%d")
    if user_data.get("last_active_day") != today_str:
        user_data["last_active_day"] = today_str
        user_data["daily_riddles_done"] = 0
        user_data["daily_scores"] = {"free": 0, "vip": 0, "premium": 0, "saturday": 0}
        user_data["hints_used_today"] = 0
        user_data["unlocked_all"] = False
    return user_data

def is_saturday():
    # UTC Saturday
    return datetime.utcnow().weekday() == 5

def show_monetag_ad(chat_id):
    if not MONETAG_KEY:
        ad_text = (
            "🔔 *Sponsored Ad*\n"
            "Enjoy Daily Riddle Wars! Support us by checking this ad.\n"
            "Support us by visiting our sponsor."
        )
        send_message(chat_id, ad_text)
        return

    ad_text = (
        "🔔 *Sponsored Ad*\n"
        "Enjoy Daily Riddle Wars! Support us by checking this ad.\n"
        "Click the button below to support us!"
    )

    keyboard = {
        "inline_keyboard": [
            [{"text": "Visit Sponsor", "url": MONETAG_KEY}]
        ]
    }

    send_message(chat_id, ad_text, reply_markup=keyboard)

# --------------------
# Command Handlers
# --------------------

def handle_start(user_id, chat_id, username):
    users = load_json(USERS_FILE)
    user = users.get(str(user_id))
    if not user:
        user = {
            "id": user_id,
            "username": username or "",
            "coins": 0,
            "hints": 0,
            "section": None,
            "daily_riddles_done": 0,
            "last_active_day": datetime.utcnow().strftime("%Y-%m-%d"),
            "daily_scores": {"free": 0, "vip": 0, "premium": 0, "saturday": 0},
            "streak": 0,
            "referrals": [],
            "referred_by": None,
            "has_paid_entry": False,
            "payment_reference": None,
            "waiting_for_answer": False,
            "current_riddle_index": 0,
            "using_hint_for_current": False,
            "coins_spent_today": 0,
            "hints_used_today": 0,
            "unlocked_all": False,
            "answered_riddles_count": 0,
        }
        users[str(user_id)] = user
        save_json(USERS_FILE, users)

    welcome_text = (
        f"👋 *Welcome to Daily Riddle Wars, {username or 'Player'}!*\n\n"
        "Choose a section to play:\n\n"
        "*Free Section*\n"
        "- Play up to 7 riddles daily for free\n"
        "- No cash prizes, just fun and leaderboard\n\n"
        "*VIP Section* (Entry Fee: ₦2000)\n"
        "- Play 7 riddles daily or unlock all 50 for ₦200\n"
        "- Prizes: 1st ₦10,000, 2nd ₦5,000, 3rd ₦3,000, 4th-10th ₦1,000 airtime\n\n"
        "*Premium Section* (Entry Fee: ₦500)\n"
        "- Play 7 riddles daily or unlock all 50 for ₦100\n"
        "- Prizes: 1st ₦5,000, 2nd ₦3,000, 3rd ₦1,000, 4th-10th ₦500 airtime\n\n"
        "*Saturday Challenge*\n"
        "- 10 hard riddles every Saturday for paid VIP/Premium players\n"
        "- Special leaderboard and prizes\n\n"
        "Use /buycoins to buy coins for hints (each hint costs 10 coins, and reduces points by 3).\n"
        "Use /leaderboard to see the leaderboard.\n"
        "Use /help for more info.\n\n"
        "Please select your section now:"
    )
    keyboard = {
        "inline_keyboard": [
            [{"text": "Free Section (No Fee)", "callback_data": "choose_free"}],
            [{"text": "VIP Section (₦2000 Entry)", "callback_data": "choose_vip"}],
            [{"text": "Premium Section (₦500 Entry)", "callback_data": "choose_premium"}],
            [{"text": "Saturday Challenge Info", "callback_data": "show_saturday_info"}],
        ]
    }
    send_message(chat_id, welcome_text, keyboard)

# The rest of your handler functions such as handle_section_choice, handle_payentry, handle_checkpayment,
# handle_play, handle_answer etc. would go here exactly as before, unchanged except to call show_monetag_ad(chat_id)
# in the relevant place to display the ad.

# For brevity, I am not repeating every handler here. You can merge your existing handlers with this setup.

# --------------------
# Flask Routes
# --------------------

@app.route("/", methods=["GET"])
def index():
    return "Daily Riddle Wars Bot is running!"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    if "message" in data:
        message = data["message"]
        chat_id = message["chat"]["id"]
        user_id = message["from"]["id"]
        username = message["from"].get("username", "")
        text = message.get("text", "")

        if text == "/start":
            handle_start(user_id, chat_id, username)
        elif text == "/play":
            handle_play(user_id, chat_id)
        elif text == "/checkpayment":
            handle_checkpayment(user_id, chat_id)
        # Add other command handlers here
        else:
            # If user is answering a riddle
            user = get_user_data(user_id)
            if user and user.get("waiting_for_answer"):
                handle_answer(user_id, chat_id, text)
            else:
                send_message(chat_id, "Unknown command or input. Use /help for commands.")

    elif "callback_query" in data:
        callback = data["callback_query"]
        chat_id = callback["message"]["chat"]["id"]
        user_id = callback["from"]["id"]
        data_cb = callback["data"]

        # Handle inline button callbacks here
        if data_cb.startswith("choose_"):
            choice = data_cb.split("_")[1]
            handle_section_choice(user_id, chat_id, choice)
        elif data_cb == "unlock_all_riddles":
            # Implement unlock logic here
            send_message(chat_id, "Unlock all riddles feature coming soon!")
        elif data_cb == "show_saturday_info":
            send_message(chat_id, "Saturday Challenge is every Saturday with 10 special riddles for VIP and Premium paid players.")
        elif data_cb == "use_hint":
            # Implement hint usage logic here
            send_message(chat_id, "Hint feature coming soon!")
        elif data_cb == "skip_riddle":
            # Implement skip riddle logic here
            send_message(chat_id, "Skip riddle feature coming soon!")
        else:
            send_message(chat_id, "Unknown action.")

    return jsonify({"status": "ok"})

# --------------------
# Main
# --------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
