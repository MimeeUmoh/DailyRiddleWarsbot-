# utils/paystack.py
# Minimal helpers to create and verify Paystack checkout sessions.
# Replace with actual Paystack API code and signature verification in production.

import os
import requests
from config import PAYSTACK_SECRET

PAYSTACK_INIT_URL = "https://api.paystack.co/transaction/initialize"
PAYSTACK_VERIFY_URL = "https://api.paystack.co/transaction/verify/{ref}"

HEADERS = {
    "Authorization": f"Bearer {PAYSTACK_SECRET}"
}

def init_payment(email: str, amount_kobo: int, callback_url: str, metadata=None):
    """
    Initialize a Paystack transaction and return checkout URL.
    amount_kobo is amount in kobo (so ₦100 => 10000).
    """
    payload = {
        "email": email,
        "amount": amount_kobo,
        "callback_url": callback_url
    }
    if metadata:
        payload["metadata"] = metadata
    resp = requests.post(PAYSTACK_INIT_URL, json=payload, headers=HEADERS, timeout=10)
    data = resp.json()
    if data.get("status"):
        return {"ok": True, "checkout_url": data["data"]["authorization_url"], "reference": data["data"]["reference"]}
    return {"ok": False, "error": data.get("message")}

def verify_payment(reference: str):
    resp = requests.get(PAYSTACK_VERIFY_URL.format(ref=reference), headers=HEADERS, timeout=10)
    return resp.json()
