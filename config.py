import os
import sys

def get_env_var(name):
    value = os.environ.get(name)
    if value is None:
        print(f"Error: Required environment variable '{name}' is not set.")
        sys.exit(1)
    return value

BOT_TOKEN = get_env_var("BOT_TOKEN")
ADMIN_USERNAME = get_env_var("ADMIN_USERNAME")
ADMIN_PASSWORD = get_env_var("ADMIN_PASSWORD")
PAYSTACK_SECRET_KEY = get_env_var("PAYSTACK_SECRET_KEY")
PAYSTACK_PUBLIC_KEY = get_env_var("PAYSTACK_PUBLIC_KEY")
MONETAG_SECRET_KEY = get_env_var("MONETAG_SECRET_KEY")
