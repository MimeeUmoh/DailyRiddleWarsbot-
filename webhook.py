# webhook.py

from flask import Blueprint, request, jsonify
import hmac
import hashlib
import json
from config import PAYSTACK_WEBHOOK_SECRET

webhook_bp = Blueprint("webhook", __name__)

@webhook_bp.route("/paystack-webhook", methods=["POST"])
def paystack_webhook():
    # Verify Paystack signature
    paystack_signature = request.headers.get("x-paystack-signature")
    payload = request.data

    computed_signature = hmac.new(
        PAYSTACK_WEBHOOK_SECRET.encode("utf-8"),
        payload,
        hashlib.sha512
    ).hexdigest()

    if computed_signature != paystack_signature:
        return jsonify({"error": "Invalid signature"}), 403

    # Parse the webhook event
    event = json.loads(payload.decode("utf-8"))
    event_type = event.get("event")
    data = event.get("data", {})

    # Example: Payment successful
    if event_type == "charge.success":
        customer_email = data.get("customer", {}).get("email")
        amount_paid = data.get("amount") / 100  # convert kobo to naira

        # TODO: Mark user as premium/VIP based on amount_paid
        print(f"Payment received from {customer_email}: ₦{amount_paid}")

    return jsonify({"status": "success"}), 200
