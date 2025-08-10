import os
import requests
import hmac
import hashlib

PAYSTACK_SECRET_KEY = os.getenv("PAYSTACK_SECRET_KEY")
if not PAYSTACK_SECRET_KEY:
    raise ValueError("PAYSTACK_SECRET_KEY environment variable not set")

BASE_URL = "https://api.paystack.co"
HEADERS = {
    "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
    "Content-Type": "application/json",
}

def initialize_payment(email: str, amount_kobo: int, metadata: dict) -> dict | None:
    """
    Initialize a payment on Paystack.
    Args:
        email: Customer email
        amount_kobo: Amount in Kobo (1 Naira = 100 Kobo)
        metadata: Dictionary with extra info (e.g., user_id, chat_id)
    Returns:
        dict with 'authorization_url' and 'reference' if success, else None
    """
    url = f"{BASE_URL}/transaction/initialize"
    payload = {
        "email": email,
        "amount": amount_kobo,
        "metadata": metadata,
    }
    try:
        resp = requests.post(url, json=payload, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if data.get("status") and data["data"].get("authorization_url"):
            return {
                "authorization_url": data["data"]["authorization_url"],
                "reference": data["data"]["reference"],
            }
    except requests.RequestException:
        pass
    return None

def verify_payment(reference: str) -> dict | None:
    """
    Verify a payment by reference.
    Args:
        reference: Paystack payment reference string
    Returns:
        Payment data dict if verified and successful, else None
    """
    url = f"{BASE_URL}/transaction/verify/{reference}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if data.get("status") and data["data"]["status"] == "success":
            return data["data"]
    except requests.RequestException:
        pass
    return None

def verify_webhook_signature(paystack_signature: str, payload_body: bytes) -> bool:
    """
    Verify webhook payload signature for security.
    Args:
        paystack_signature: Signature from Paystack webhook header
        payload_body: Raw request body bytes
    Returns:
        True if signatures match, else False
    """
    computed_signature = hmac.new(
        PAYSTACK_SECRET_KEY.encode('utf-8'),
        msg=payload_body,
        digestmod=hashlib.sha512
    ).hexdigest()
    return hmac.compare_digest(computed_signature, paystack_signature)

