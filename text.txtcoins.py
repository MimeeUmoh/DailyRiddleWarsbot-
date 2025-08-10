# coins.py
import json
import os

DATA_DIR = "data"
USERS_FILE = os.path.join(DATA_DIR, "users.json")

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def get_coins(user_id):
    users = load_users()
    user = users.get(user_id)
    if not user:
        return 0
    return user.get("coins", 0)

def add_coins(user_id, amount):
    if amount <= 0:
        return False
    users = load_users()
    user = users.get(user_id)
    if not user:
        return False
    user["coins"] = user.get("coins", 0) + amount
    save_users(users)
    return True

def deduct_coins(user_id, amount):
    if amount <= 0:
        return False
    users = load_users()
    user = users.get(user_id)
    if not user:
        return False
    current = user.get("coins", 0)
    if current < amount:
        return False
    user["coins"] = current - amount
    save_users(users)
    return True
