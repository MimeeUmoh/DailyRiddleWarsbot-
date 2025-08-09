# webhook.py
# Flask blueprint for Paystack webhook handling

from flask import Blueprint, request, jsonify
from utils.paystack import verify_payment
from utils import load_users, save_json, save_users, load_json
from referrals import reward_referrer_on_purchase
from config import PAYSTACK_SECRET

webhook_bp = Blueprint("webhook", __name__)

@webhook_bp.route("/paystack_webhook", methods=["POST"])
def paystack_webhook():
    """
    Simple webhook. In production verify signatures (X-Paystack-Signature header).
    Payload contains: event, data (including reference and metadata you passed).
    """
    payload = request.get_json(force=True)
    # TODO: verify signature using PAYSTACK_SECRET
    event = payload.get("event")
    data = payload.get("data", {})

    if event == "charge.success":
        # Example: metadata should include user_id and action (unlock_vip/unlock_premium/buy_coins)
        metadata = data.get("metadata", {})
        reference = data.get("reference")
        status = data.get("status")
        if status == "success":
            user_id = str(metadata.get("user_id"))
            action = metadata.get("action")
            users = load_users()
            user = users.get(user_id)
            if user:
                if action == "unlock_vip":
                    user["is_vip"] = True
                elif action == "unlock_premium":
                    user["is_premium"] = True
                elif action and action.startswith("buy_coins_"):
                    try:
                        coins = int(action.split("_")[-1])
                        user["coins"] = user.get("coins", 0) + coins
                    except:
                        pass
                # mark maybe paid
                user["paid"] = True
                save_users(users)
                # Reward referrer if exists
                reward_referrer_on_purchase(user_id)
    return jsonify({"status": "ok"})
