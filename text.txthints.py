# hints.py
import json
import os

DATA_DIR = "data"
USERS_FILE = os.path.join(DATA_DIR, "users.json")

HINT_COST = 10  # coins per hint

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def can_use_hint(user_id):
    users = load_users()
    user = users.get(user_id)
    if not user:
        return False, "User not found."
    coins = user.get("coins", 0)
    if coins < HINT_COST:
        return False, "Not enough coins for a hint."
    return True, ""

def use_hint(user_id):
    users = load_users()
    user = users.get(user_id)
    if not user:
        return False, "User not found."

    coins = user.get("coins", 0)
    if coins < HINT_COST:
        return False, "Not enough coins."

    user["coins"] = coins - HINT_COST
    save_users(users)
    return True, f"Hint used! {HINT_COST} coins deducted. Coins left: {user['coins']}"
