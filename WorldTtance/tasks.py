import requests
import time
import hmac
import hashlib
import os
import urllib.parse
from celery import shared_task
from django.conf import settings


BINANCE_BASE_URL = "https://testnet.binance.vision"
binance_wallet = settings.BINANCE_ADMIN_WALLET
api_key = binance_wallet["api_key"]
api_secret = binance_wallet["api_secret"]
wallet_address = binance_wallet["wallet_address"]  # Get wallet address

def generate_binance_signature(params):
    query_string = urllib.parse.urlencode(params)
    return hmac.new(
        BINANCE_SECRET_KEY.encode(),
        query_string.encode(),
        hashlib.sha256
    ).hexdigest()

@shared_task
def check_binance_transaction(transaction_id):
    timestamp = int(time.time() * 1000)
    params = {
        "transactionId": transaction_id,
        "timestamp": timestamp,
    }

    signature = generate_binance_signature(params)
    params["signature"] = signature

    headers = {
        "X-MBX-APIKEY": BINANCE_API_KEY,
        "Content-Type": "application/json"
    }

    response = requests.get(f"{BINANCE_API_URL}/sapi/v1/capital/withdraw/history", headers=headers, params=params)
    
    try:
        response_data = response.json()

        if "success" in response_data and response_data["success"]:
            print(f" Transaction {transaction_id} completed successfully!")
        else:
            print(f" Transaction {transaction_id} failed.")

    except requests.exceptions.RequestException as e:
        print(f"⚠️ Binance API request failed: {e}")
