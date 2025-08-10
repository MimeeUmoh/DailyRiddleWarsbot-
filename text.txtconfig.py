import os

# Payment
PAYSTACK_SECRET_KEY = os.getenv("PAYSTACK_SECRET_KEY")
PAYSTACK_PUBLIC_KEY = os.getenv("PAYSTACK_PUBLIC_KEY")

# Monetag Ads
MONETAG_KEY = os.getenv("MONETAG_KEY")  # For free user ads

# Other configs
DATA_DIR = os.getenv("DATA_DIR", "data")
