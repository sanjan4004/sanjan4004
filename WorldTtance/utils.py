import requests
import time
import hashlib
import hmac
import json
import logging
import requests
import urllib.parse
from django.conf import settings
from django.core.mail import send_mail
from decimal import Decimal
from .models import AdminWallet, Transaction
from django.db import transaction
from django.db import transaction as db_transaction  #  Avoids naming conflict
from .models import ExchangeRate


logger = logging.getLogger(__name__)

def get_exchange_rate(source_currency, target_currency):
    """
    Fetches the exchange rate between source and target currency.
    Falls back to default rate if API fails.
    """
    if source_currency == target_currency:
        return 1.0

    try:
        response = requests.get(
            f"https://api.exchangerate.host/latest",
            params={"base": source_currency, "symbols": target_currency},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        rate = data["rates"].get(target_currency)
        if rate:
            logger.info(f"Fetched exchange rate {source_currency} → {target_currency}: {rate}")
            return float(rate)
        else:
            logger.warning(f"No rate found for {source_currency} → {target_currency}")
            raise ValueError("Exchange rate unavailable")

    except Exception as e:
        logger.error(f"Exchange rate API failed: {e}")

        # Fallback to default if available
        fallback_rate = settings.DEFAULT_EXCHANGE_RATES.get(source_currency)
        if fallback_rate:
            logger.warning(f"Using fallback rate for {source_currency} → {target_currency}: {fallback_rate}")
            return float(fallback_rate)

        raise RuntimeError("Exchange rate fetch failed and no fallback available.")


binance_wallet = settings.BINANCE_ADMIN_WALLET
api_key = binance_wallet["api_key"]
api_secret = binance_wallet["api_secret"]
wallet_address = binance_wallet["wallet_address"]  #Get wallet address


# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def send_transaction_email(user_email, transaction_details):
    """Sends an email confirmation for a transaction."""
    subject = "Transaction Successful"
    message = f"Your transaction was successful!\nDetails: {transaction_details}"
    from_email = "no-reply@yourdomain.com"
    send_mail(subject, message, from_email, [user_email])
    
def generate_binance_signature(params, api_secret):
    query_string = "&".join([f"{key}={value}" for key, value in sorted(params.items())])
    return hmac.new(api_secret.encode(), query_string.encode(), hashlib.sha256).hexdigest()



def send_binance_payment(amount, crypto_symbol, recipient_wallet):
    """
    Transfers crypto from the admin Binance account to the recipient's wallet.
    """
    endpoint = f"{BINANCE_BASE_URL}/sapi/v1/capital/withdraw/apply"
    timestamp = int(time.time() * 1000)

    payload = {
        "coin": crypto_symbol,
        "address": recipient_wallet,
        "amount": amount,
        "network": "BSC",
        "timestamp": timestamp
    }

    query_string = urllib.parse.urlencode(sorted(payload.items()))
    signature = generate_binance_signature(query_string)
    payload["signature"] = signature

    headers = {"X-MBX-APIKEY": BINANCE_API_KEY}
    response = requests.post(endpoint, headers=headers, params=payload)
    
    try:
        response_data = response.json()
    except json.JSONDecodeError:
        logger.critical(f"Binance API returned non-JSON response: {response.text}")
        return {"success": False, "error": "Invalid response from Binance"}
    
    if response.status_code == 200 and "tranId" in response_data:
        return {"success": True, "transaction_id": response_data["tranId"]}
    else:
        return {"success": False, "error": response_data.get("msg", "Transaction failed")}

#Helper function to convert currencies to cryptocurrency
def convert_currency_to_crypto(amount, currency):
    conversion_rates = {"USD": "USDT", "EUR": "BUSD", "GBP": "BTC"}
    return amount, conversion_rates.get(currency.upper(), "USDT")


def send_bitcoin_payment(amount, recipient_wallet):
    """Send Bitcoin payment using Binance API."""
    return send_binance_payment(amount, "BTC", recipient_wallet)



logger = logging.getLogger(__name__)
# Load Binance API credentials securely
BINANCE_WALLET = getattr(settings, "BINANCE_ADMIN_WALLET", {})
API_KEY = BINANCE_WALLET.get("api_key")
API_SECRET = BINANCE_WALLET.get("api_secret")
WALLET_ADDRESS = BINANCE_WALLET.get("wallet_address")  # Ensure this is actually used!

#  Set Binance API URL based on environment
BINANCE_API_URL = "https://testnet.binance.vision/sapi/v1/asset/transfer"  # Testnet
#BINANCE_API_URL = "https://api.binance.com/sapi/v1/asset/transfer"  # Live API

logger.info(f"🔑 API_KEY: {API_KEY}, WALLET_ADDRESS: {WALLET_ADDRESS}")



def transfer_fees_to_binance(amount, currency):
    """
    Transfers collected transaction fees to the Binance Admin Wallet.
    """
    try:
        #  Check if credentials exist
        if not API_KEY or not API_SECRET:
            logger.critical(" Binance API credentials are missing in settings.py")
            return {"success": False, "error": "Missing Binance API credentials"}

        #  Create request payload
        payload = {
            "type": "MAIN_UMFUTURE",  # Example: Transfer from Main account to Futures
            "asset": currency.upper(),  # Binance requires uppercase asset codes (e.g., "USDT")
            "amount": str(amount),  # Convert amount to string
            "timestamp": int(time.time() * 1000)  # Binance requires a timestamp
        }

        #  Generate API Signature
        query_string = urllib.parse.urlencode(payload, doseq=True)
        signature = hmac.new(API_SECRET.encode(), query_string.encode(), hashlib.sha256).hexdigest()
        payload["signature"] = signature

        #  Set headers
        headers = {"X-MBX-APIKEY": API_KEY}

        #  Send request to Binance API
        response = requests.post(BINANCE_API_URL, params=payload, headers=headers)

        #  Log full response for debugging
        logger.info(f" Binance API Response: {response.status_code} - {response.text}")

        #  Handle JSON response safely
        try:
            response_data = response.json()
        except json.JSONDecodeError:
            logger.critical(" Binance API returned non-JSON response: " + response.text)
            return {"success": False, "error": "Invalid response from Binance"}

        #  Validate response format
        if not isinstance(response_data, dict):
            logger.critical(" Unexpected response format from Binance API")
            return {"success": False, "error": "Unexpected response format from Binance"}

        #  Check for Binance API errors
        if "code" in response_data and response_data["code"] != 200:
            error_msg = response_data.get("msg", "Unknown error")
            logger.critical(f" Binance API Error: {error_msg}")

            #  Retry logic for rate limits
            if response_data["code"] in [-1003, -1015]:  # Rate limit errors
                logger.warning(" Binance API Rate Limit Hit. Retrying in 5 seconds...")
                time.sleep(5)
                return transfer_fees_to_binance(amount, currency)  # Retry once

            return {"success": False, "error": error_msg}

        #  Success response
        if "tranId" in response_data:
            return {"success": True, "message": f"Transaction fee transferred successfully! TxID: {response_data['tranId']}"}
        
        return {"success": False, "error": "Unknown Binance API response"}
        logger.info(f"🚀 Transferring {amount} {currency.upper()} to Binance Wallet")
    except requests.exceptions.RequestException as e:
        logger.critical(f" Binance Transfer Error: {str(e)}", exc_info=True)
        return {"success": False, "error": str(e)}



#  Load Binance API credentials securely
BINANCE_WALLET = getattr(settings, "BINANCE_ADMIN_WALLET", {})
API_KEY = BINANCE_WALLET.get("api_key")
API_SECRET = BINANCE_WALLET.get("api_secret")
WALLET_ADDRESS = BINANCE_WALLET.get("wallet_address")  # Ensure this is actually used!


logger = logging.getLogger(__name__)

def transfer_fees_to_admin(transaction_id):
    """
    Transfers the transaction fee to the Binance Admin Wallet.
    Uses database locking to prevent duplicate fee transfers.
    """
    try:
        with db_transaction.atomic():  #  Prevents race conditions
            #  Lock the transaction row to avoid race conditions
            txn = Transaction.objects.select_for_update().filter(id=transaction_id).first()

            if not txn:
                logger.error(f" Transaction with ID {transaction_id} not found.")
                return {"success": False, "error": f"Transaction with ID {transaction_id} not found."}

            #  Prevent duplicate transfers
            if txn.fee_transferred:
                logger.warning(f" Fee already transferred for Transaction {transaction_id}. Skipping.")
                return {"success": False, "error": "Fee already transferred."}

            #  Validate transaction fee
            if txn.transaction_fee is None or txn.currency is None:
                return {"success": False, "error": "Invalid transaction fee or missing currency"}

            if txn.transaction_fee <= 0:
                return {"success": False, "error": "Transaction fee must be greater than zero"}

            #  Convert fee to Binance format (up to 8 decimal places)
            amount = str(Decimal(txn.transaction_fee).quantize(Decimal("0.00000001")))
            currency = txn.currency.upper()

            #  Ensure currency is valid
            valid_currencies = {"USD", "EUR", "BTC", "ETH", "BNB", "USDT", "KES"}  # Add more if needed
            if currency not in valid_currencies:
                return {"success": False, "error": f"Unsupported currency: {currency}"}

            #  Transfer fees to Binance Admin Wallet
            response = transfer_fees_to_binance(amount, currency)

            if not response or "error" in response:
                logger.error(f" Binance Fee Transfer Failed for Transaction {transaction_id}: {response}")
                return {"success": False, "error": response.get("error", "Unknown error from Binance")}

            #  Mark fee as transferred in the database
            txn.fee_transferred = True
            txn.save(update_fields=["fee_transferred"])  #  Optimized update

            logger.info(f" Fee transferred successfully for Transaction {transaction_id}.")
            return {"success": True, "message": "Fee transferred successfully"}

    except Exception as e:
        logger.critical(f" Critical Error in transfer_fees_to_admin: {str(e)}", exc_info=True)
        return {"success": False, "error": str(e)}
        
def process_transaction_fee(amount, currency):
    """
    Transfers collected transaction fees to the Binance Admin Wallet.
    """
    admin_wallet = AdminWallet.objects.first()
    if not admin_wallet:
        return {"success": False, "error": "AdminWallet not found"}

    headers = {"Authorization": f"Bearer {api_secret}"}
    payload = {
        "recipient": admin_wallet.wallet_address,
        "amount": amount,
        "currency": currency
    }

    try:
        response = requests.post("https://api.binance.com/v3/withdraw", json=payload, headers=headers)
        response.raise_for_status()  # Raise error for failed requests
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Binance Transaction Fee Transfer Failed: {str(e)}")
        return {"success": False, "error": "Failed to transfer fees to Binance"}


import logging
import requests
from datetime import datetime

logger = logging.getLogger(__name__)

# Local Node.js backend URL (replace with your actual backend if needed)
NODE_BACKEND_URL ="http://127.0.0.1:5000/pay/api/flutterwave/process-payments"

def generate_transaction_reference():
    """Generate a unique transaction reference using timestamp."""
    return f"WT-{datetime.now().strftime('%Y%m%d%H%M%S%f')[:-3]}"  # TXN-YYYYMMDDHHMMSSmmm

def send_transaction_to_node(transaction):
    """
    Sends transaction details to the Node.js backend for payment processing.
    Returns the response from the backend.
    """
    # Ensure transaction_reference is set
    if not transaction.transaction_reference:
        transaction.transaction_reference = generate_transaction_reference()
        transaction.save()

    # Ensure recipient details are available
    recipient_name = transaction.recipient.full_name if transaction.recipient else "Unknown"
    recipient_account = transaction.recipient.account_number if transaction.recipient else "N/A"

    payload = {
        "transaction_id": str(transaction.id),
        "user_id": str(transaction.user.id),
        "amount": float(transaction.amount),  # Ensure it's a float
        "currency": transaction.currency,
        "recipient": recipient_name,
        "recipient_account": recipient_account,
        "payment_method": transaction.payment_method,
        "transaction_reference": transaction.transaction_reference
    }

    try:
        logger.info(f"Sending transaction {transaction.transaction_reference} to Node.js: {payload}")
        response = requests.post(NODE_BACKEND_URL, json=payload, timeout=15)
        response_data = response.json()
        
        if response.status_code == 200 and response_data.get("status") == "success":
            logger.info(f"Transaction {transaction.transaction_reference} processed successfully.")
            return response_data
        else:
            logger.error(f"Transaction processing failed: {response_data}")
            return {"status": "error", "message": response_data.get("message", "Unknown error")}

    except requests.RequestException as e:
        logger.error(f"Failed to communicate with Node.js backend: {e}")
        return {"status": "error", "message": str(e)}
