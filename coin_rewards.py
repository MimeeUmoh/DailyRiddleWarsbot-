import json
from datetime import datetime, timedelta

USERS_FILE = "data/users.json"

def load_users():
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

def give_daily_login_bonus(user_id):
    users = load_users()
    user = users.get(user_id)
    if not user:
        return "User not found."

    today = datetime.utcnow().date().isoformat()
    last_login = user.get("last_login")
    
    if last_login == today:
        return "Already claimed today."

    # Update coin balance
    user["coins"] = user.get("coins", 0) + 5
    user["last_login"] = today

    # Handle streaks
    yesterday = (datetime.utcnow() - timedelta(days=1)).date().isoformat()
    if user.get("last_login") == yesterday:
        user["streak"] = user.get("streak", 0) + 1
    else:
        user["streak"] = 1

    # Streak rewards
    streak = user["streak"]
    if streak == 3:
        user["coins"] += 10
    elif streak == 5:
        user["coins"] += 25
    elif streak == 7:
        user["coins"] += 40

    users[user_id] = user
    save_users(users)
    return f"Daily bonus added! Streak: {streak} days"

