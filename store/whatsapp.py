import requests
from django.conf import settings


def is_configured():
    return bool(settings.WA_PHONE_NUMBER_ID and settings.WA_ACCESS_TOKEN and settings.WA_ADMIN_TO)


def send_text(to_phone: str, message: str):
    url = f"https://graph.facebook.com/v19.0/{settings.WA_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {settings.WA_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to_phone,
        "type": "text",
        "text": {"body": message},
    }

    r = requests.post(url, headers=headers, json=payload, timeout=20)

    # If something is wrong, show the error body instead of silently failing
    try:
        data = r.json()
    except Exception:
        data = {"raw": r.text}

    r.raise_for_status()
    return data

def debug_phone_number():
    url = f"https://graph.facebook.com/v19.0/{settings.WA_PHONE_NUMBER_ID}"
    headers = {"Authorization": f"Bearer {settings.WA_ACCESS_TOKEN}"}

    r = requests.get(url, headers=headers, timeout=20)

    try:
        data = r.json()
    except Exception:
        data = {"raw": r.text}

    r.raise_for_status()
    return data