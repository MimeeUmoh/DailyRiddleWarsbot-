# utils.py
# Generic helpers used by app.py and other modules

import json
import os
from typing import Any

from config import USERS_FILE, SCORES_FILE, REFERRALS_FILE, RIDDLES_FOLDER

def load_json(path: str) -> Any:
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path: str, data: Any) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# User helpers
def load_users():
    return load_json(USERS_FILE)

def save_users(users):
    save_json(USERS_FILE, users)

def get_user(user_id: str):
    users = load_users()
    return users.get(user_id)

def ensure_user(user_id: str, template=None):
    users = load_users()
    if user_id not in users:
        users[user_id] = template or {
            "name": None,
            "phone": None,
            "account_number": None,
            "bank": None,
            "coins": 0,
            "is_vip": False,
            "is_premium": False,
            "progress": {"free": 0, "vip": 0, "premium": 0},
            "answered": {},   # riddle_id -> {"score": 10/7, "used_hint": bool}
            "streak": 0,
            "last_login": None,
            "paid": False,
            "referrer": None
        }
        save_users(users)
    return users[user_id]

# Riddle helpers
def list_riddle_file(pack_name: str) -> str:
    # returns path for a pack: e.g. data/riddles/free.json
    return os.path.join(RIDDLES_FOLDER, f"{pack_name}.json")

def load_riddle_pack(pack_name: str):
    path = list_riddle_file(pack_name)
    return load_json(path) or []

def get_riddle_by_index(pack_name: str, index: int):
    pack = load_riddle_pack(pack_name)
    if index < 0 or index >= len(pack):
        return None
    return pack[index]

def check_answer(riddle, answer: str) -> bool:
    if not riddle:
        return False
    correct = riddle.get("answer", "").strip().lower()
    return correct == (answer or "").strip().lower()

# Score update helper
def apply_answer(user_id: str, riddle_id: str, score: int, used_hint=False):
    users = load_users()
    user = users.get(user_id)
    if not user:
        return False
    user.setdefault("answered", {})
    user["answered"][riddle_id] = {"score": score, "used_hint": bool(used_hint)}
    save_users(users)
    return True
