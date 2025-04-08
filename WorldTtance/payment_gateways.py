import requests
import logging
import hmac
import hashlib
import time
from django.conf import settings
from .models import Transaction

# Logging Configuration
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Payment API Configurations
PAYMENT_APIS = {
    "Google Pay": "https://api.googlepay.com/payments",
    "Apple Pay": "https://api.applepay.com/payments",
    "Cryptocurrency": "https://api.crypto.com/v1/payments",
    "Bank Transfer": "https://api.banktransfer.com/initiate",
    "M-Pesa": "https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest",
    "Binance": "https://api.binance.com/sapi/v1/pay",
    "Mobile Wallet": "https://api.mobilewallet.com/pay",
}

# Fetch Binance API keys from settings
binance_wallet = settings.BINANCE_ADMIN_WALLET
api_key = binance_wallet.get("api_key")
api_secret = binance_wallet.get("api_secret")
wallet_address = binance_wallet.get("wallet_address")


def process_payments(payment_method, amount, currency, recipient_details):
    """
    Processes a payment based on the selected payment method.
    
    :param payment_method: The selected payment method (e.g., "Google Pay", "Binance").
    :param amount: The transaction amount.
    :param currency: The currency of the transaction.
    :param recipient_details: Dictionary containing recipient info.
    :return: JSON response from the payment API or an error message.
    """
    logger.info(f"🔄 Processing {payment_method} payment for {amount} {currency}")

    url = PAYMENT_APIS.get(payment_method)
    
    if not url:
        logger.error(f" Invalid payment method: {payment_method}")
        return {"status": "failed", "message": "Invalid payment method"}

    payload = {
        "amount": str(amount),  # Ensure decimal precision
        "currency": currency.upper(),  # Standardize currency format
        "recipient": recipient_details,
    }

    headers = {
        "Authorization": f"Bearer {get_api_key(payment_method)}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)  #  Set timeout
        response.raise_for_status()  # Raise an error for non-200 responses
        
        result = response.json()
        logger.info(f" Payment successful: {result}")

        #  Save the transaction to DB
        save_transaction(payment_method, amount, currency, recipient_details, result)

        return result

    except requests.exceptions.Timeout:
        logger.error(f" Payment API timeout for {payment_method}")
        return {"status": "failed", "message": "Payment API timeout. Try again later."}

    except requests.exceptions.RequestException as e:
        logger.error(f" Payment processing failed for {payment_method}: {str(e)}")
        return {"status": "failed", "message": str(e)}


def get_api_key(payment_method):
    """Dynamically fetch API keys based on payment method."""
    api_keys = {
        "Binance": api_key,
        "Google Pay": settings.GPAY_API_KEY,
        "Apple Pay": settings.APPLE_PAY_API_KEY,
        "Cryptocurrency": settings.CRYPTO_API_KEY,
        "Bank Transfer": settings.BANK_API_KEY,
        "M-Pesa": settings.MPESA_API_KEY,
        "Mobile Wallet": settings.MOBILE_WALLET_API_KEY,
    }
    return api_keys.get(payment_method, "default_api_key")  # Default fallback if key is missing


def save_transaction(payment_method, amount, currency, recipient_details, response_data):
    """
    Save the transaction details to the database.
    
    :param payment_method: The payment method used.
    :param amount: The transaction amount.
    :param currency: The currency of the transaction.
    :param recipient_details: The recipient information.
    :param response_data: The API response from the payment gateway.
    """
    try:
        Transaction.objects.create(
            payment_method=payment_method,
            amount=amount,
            currency=currency,
            recipient=recipient_details.get("recipient_name", "Unknown"),
            status=response_data.get("status", "failed"),
            transaction_id=response_data.get("transaction_id", ""),
            response_message=response_data.get("message", ""),
        )
        logger.info(f" Transaction saved successfully: {payment_method} - {amount} {currency}")
    except Exception as e:
        logger.error(f" Failed to save transaction: {str(e)}")


###  Binance Payment Processing with Secure API Signature
def process_binance_payment(amount, currency, recipient_address):
    """
    Process a payment via Binance API.
    
    :param amount: The amount to send.
    :param currency: The currency (e.g., "USDT").
    :param recipient_address: The recipient's Binance wallet address.
    :return: JSON response.
    """
    logger.info(f"🔄 Processing Binance payment: {amount} {currency} to {recipient_address}")

    binance_url = "https://api.binance.com/sapi/v1/asset/transfer"
    timestamp = int(time.time() * 1000)  # Binance requires a timestamp

    query_string = f"amount={amount}&currency={currency}&recipient={recipient_address}&timestamp={timestamp}"
    signature = hmac.new(api_secret.encode(), query_string.encode(), hashlib.sha256).hexdigest()

    headers = {
        "X-MBX-APIKEY": api_key,
        "Content-Type": "application/json",
    }

    payload = {
        "amount": str(amount),
        "currency": currency,
        "recipient": recipient_address,
        "signature": signature,
    }

    try:
        response = requests.post(binance_url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"🚨 Binance payment failed: {str(e)}")
        return {"status": "failed", "message": str(e)}
