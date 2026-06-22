import json
import os
import random
import time
import logging

logger = logging.getLogger(__name__)

OTP_FILE = os.path.join(os.path.dirname(__file__), '../../data/otps.json')

def load_otps() -> dict:
    """Load all generated OTPs from file."""
    if not os.path.exists(OTP_FILE):
        return {}
    try:
        with open(OTP_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error reading OTP file: {e}")
        return {}

def save_otps(data: dict):
    """Save OTP data to file."""
    os.makedirs(os.path.dirname(OTP_FILE), exist_ok=True)
    try:
        with open(OTP_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Error saving OTP file: {e}")

def generate_otp(user_id: int, username: str) -> str:
    """
    Generate a 6-digit OTP, store it with a 5-minute expiration,
    and return it.
    """
    otp = f"{random.randint(100000, 999999)}"
    expires_at = int(time.time()) + 300 # 5 minutes from now
    
    otps = load_otps()
    otps[str(user_id)] = {
        "otp": otp,
        "username": username.lower() if username else "",
        "expires_at": expires_at
    }
    save_otps(otps)
    return otp
