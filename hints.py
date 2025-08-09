# hints.py
# Handles hint logic and coin deduction

from config import PRICES
from utils import load_users, save_users, get_user, apply_answer, load_riddle_pack

def can_afford_hint(user_id: str) -> bool:
    users = load_users()
    user = users.get(user_id)
    return user and user.get("coins", 0) >= PRICES["hint_cost_coins"]

def use_hint(user_id: str, pack: str, index: int) -> dict:
    """
    Deducts coins and returns hint text for the riddle.
    Returns dict: {"ok": True/False, "error": str, "hint": str}
    """
    users = load_users()
    user = users.get(user_id)
    if not user:
        return {"ok": False, "error": "user_not_found"}
    if user.get("coins", 0) < PRICES["hint_cost_coins"]:
        return {"ok": False, "error": "not_enough_coins"}

    # Deduct coins
    user["coins"] -= PRICES["hint_cost_coins"]
    save_users(users)

    # Get hint
    riddle_pack = load_riddle_pack(pack)
    if index < 0 or index >= len(riddle_pack):
        return {"ok": False, "error": "riddle_not_found"}

    hint_text = riddle_pack[index].get("hint", "")
    return {"ok": True, "hint": hint_text}
