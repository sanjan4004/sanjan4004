import requests
from django.conf import settings

# Load API keys from Django settings
FLW_SECRET_KEY = settings.FLUTTERWAVE_SECRET_KEY
FLW_BASE_URL = settings.FLUTTERWAVE_BASE_URL

def flutterwave_payout(amount, recipient_account, recipient_name, recipient_bank, currency="NGN"):
    """
    Process a payout using Flutterwave API.

    :param amount: Amount to be sent.
    :param recipient_account: Bank or mobile wallet account number.
    :param recipient_name: Name of the recipient.
    :param recipient_bank: Bank code or mobile money provider code.
    :param currency: Transaction currency (default is "NGN").
    :return: Response JSON from Flutterwave.
    """
    
    url = f"{FLW_BASE_URL}/transfers"
    
    headers = {
        "Authorization": f"Bearer {FLW_SECRET_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "account_bank": recipient_bank,  # Example: '044' for Access Bank
        "account_number": recipient_account,
        "amount": amount,
        "currency": currency,  # NGN, KES, UGX, GHS, etc.
        "narration": f"Payout to {recipient_name}",
        "reference": f"WORLDT_{recipient_account}_{amount}",  # Unique transaction reference
        "callback_url": "https://yourdomain.com/payment/callback"
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": str(e)}
