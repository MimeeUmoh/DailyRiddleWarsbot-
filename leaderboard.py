import json

USERS_FILE = "data/users.json"
LEADERBOARD_FILE = "data/leaderboard.json"
SATURDAY_RIDDLE_IDS = list(range(41, 51))  # IDs 41–50 are Saturday riddles

def load_json(filepath):
    with open(filepath, "r") as f:
        return json.load(f)

def save_json(filepath, data):
    with open(filepath, "w") as f:
        json.dump(data, f, indent=4)

def calculate_leaderboard():
    users = load_json(USERS_FILE)
    leaderboard = []

    for user_id, user_data in users.items():
        if not user_data.get("is_vip") and not user_data.get("is_premium"):
            continue

        score = 0
        for riddle_id_str, ans_data in user_data.get("answered", {}).items():
            score += ans_data.get("score", 0)

        leaderboard.append({
            "user_id": user_id,
            "username": user_data.get("username", "Unknown"),
            "total_score": score
        })

    leaderboard.sort(key=lambda x: x["total_score"], reverse=True)
    save_json(LEADERBOARD_FILE, leaderboard)

def calculate_saturday_winners():
    users = load_json(USERS_FILE)
    saturday_board = []

    for user_id, user_data in users.items():
        score = 0
        for riddle_id in SATURDAY_RIDDLE_IDS:
            ans_data = user_data.get("answered", {}).get(str(riddle_id), {})
            score += ans_data.get("score", 0)

        if score > 0:
            saturday_board.append({
                "user_id": user_id,
                "username": user_data.get("username", "Unknown"),
                "saturday_score": score
            })

    saturday_board.sort(key=lambda x: x["saturday_score"], reverse=True)
    return saturday_board  # This part is used for payout

