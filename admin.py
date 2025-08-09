# admin.py
# Simple CLI utilities for marking payments and exporting winners

import csv
from utils import load_json, save_json
from config import USERS_FILE, SCORES_FILE, WINNERS_CSV

def export_winners_csv(output_path=WINNERS_CSV, top_n=10):
    scores = load_json(SCORES_FILE)
    users = load_json(USERS_FILE)
    # Score structure: {date: {user_id: score}} or {user_id: {"total_score": X}}
    # We'll attempt to flatten: check if top structure is dates
    flat = {}
    if isinstance(scores, dict) and scores:
        sample_v = next(iter(scores.values()))
        if isinstance(sample_v, dict):
            # daily keyed structure: aggregate totals
            for date, day_scores in scores.items():
                for uid, sc in day_scores.items():
                    flat[uid] = flat.get(uid, 0) + sc
        else:
            # assume scores is map of user_id -> {"total_score": X}
            for uid, s in scores.items():
                if isinstance(s, dict) and "total_score" in s:
                    flat[uid] = s["total_score"]
                else:
                    flat[uid] = int(s or 0)
    # sort
    sorted_list = sorted(flat.items(), key=lambda x: x[1], reverse=True)[:top_n]
    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["username", "telegram_id", "phone", "bank", "total_score", "paid"])
        for uid, total in sorted_list:
            user = users.get(uid, {})
            writer.writerow([
                user.get("name", ""),
                uid,
                user.get("phone", ""),
                user.get("bank", ""),
                total,
                "Yes" if user.get("paid") else "No"
            ])
    print(f"Exported top {top_n} to {output_path}")

def mark_user_paid(user_id):
    users = load_json(USERS_FILE)
    if user_id in users:
        users[user_id]["paid"] = True
        save_json(USERS_FILE, users)
        print(f"Marked {user_id} as paid")
    else:
        print("User not found")
