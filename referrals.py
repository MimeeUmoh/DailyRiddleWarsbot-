import json

REFERRALS_FILE = "data/referrals.json"
USERS_FILE = "data/users.json"

def load_json(filepath):
    with open(filepath, "r") as f:
        return json.load(f)

def save_json(filepath, data):
    with open(filepath, "w") as f:
        json.dump(data, f, indent=4)

def register_referral(referrer_id, referred_id):
    data = load_json(REFERRALS_FILE)

    if referred_id in data:
        return False  # Already referred

    data[referred_id] = {
        "referrer": referrer_id,
        "bonus_given": False
    }

    save_json(REFERRALS_FILE, data)
    return True

def reward_referrer_on_purchase(referred_id):
    referrals = load_json(REFERRALS_FILE)
    users = load_json(USERS_FILE)

    if referred_id not in referrals:
        return

    referral_info = referrals[referred_id]
    if referral_info["bonus_given"]:
        return

    referrer_id = referral_info["referrer"]

    # Give bonus
    if referrer_id in users:
        users[referrer_id]["coins"] += 10
        referrals[referred_id]["bonus_given"] = True
        save_json(REFERRALS_FILE, referrals)
        save_json(USERS_FILE, users)

def get_referrer(referred_id):
    data = load_json(REFERRALS_FILE)
    return data.get(referred_id, {}).get("referrer")
