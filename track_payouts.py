import json
from datetime import datetime

PAYOUT_LOG_FILE = "payouts.json"

def log_payout(username, amount, method):
    try:
        with open(PAYOUT_LOG_FILE, "r") as f:
            payouts = json.load(f)
    except FileNotFoundError:
        payouts = []

    payout_entry = {
        "username": username,
        "amount": amount,
        "method": method,  # "bank" or "airtime"
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    payouts.append(payout_entry)

    with open(PAYOUT_LOG_FILE, "w") as f:
        json.dump(payouts, f, indent=4)

    print(f"Payout logged for {username}: {amount} via {method}")

# Example use
if __name__ == "__main__":
    log_payout("test_user", 500, "bank")
