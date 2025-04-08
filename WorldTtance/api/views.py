from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
import json, hmac, hashlib
from django.conf import settings
from WorldTtance.models import Transaction, AdminWallet
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from WorldTtance.models import Recipient, Transaction,UserProfile,KYCVerification,AdminWallet
from django.http import HttpResponse
from WorldTtance.forms import RecipientForm, TransactionForm,KYCVerificationForm,UserProfileForm, UserUpdateForm,UserRegisterForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
import json
from django.http import JsonResponse
from WorldTtance.choices import PAYMENT_METHODS, COUNTRIES,CURRENCY_CHOICES,CRYPTO_CHOICES
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from WorldTtance.utils import send_transaction_email,transfer_fees_to_admin,send_bitcoin_payment,process_transaction_fee,generate_binance_signature,send_binance_payment,convert_currency_to_crypto,transfer_fees_to_admin
from django.conf import settings
from decimal import Decimal
from django.urls import reverse
import uuid
from django.core.files.base import ContentFile
from WorldTtance.views import process_payment
from binance.client import Client
from binance.exceptions import BinanceAPIException
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import logging
import requests 
import os
from django.views.decorators.http import require_POST
from rest_framework.decorators import api_view
from rest_framework.response import Response
import hmac
import hashlib
from rest_framework import generics
from WorldTtance.serializers import AdminWalletSerializer  #  Correct relative import
from rest_framework.permissions import IsAdminUser
from django.core.paginator import Paginator
from rest_framework.views import APIView
from rest_framework import status
from WorldTtance.serializers import RecipientSerializer
from rest_framework.permissions import IsAuthenticated
from django.template.loader import get_template
from django.http import HttpResponseNotFound
from django.db import transaction as db_transaction
import time
import random
from WorldTtance.utils import send_transaction_to_node  # Ensure this function exists




# Initialize Binance client
BINANCE_API_URL = settings.BINANCE_API_BASE_URL
binance_wallet = settings.BINANCE_ADMIN_WALLET
api_key = binance_wallet["api_key"]
api_secret = binance_wallet["api_secret"]
wallet_address = binance_wallet["wallet_address"]  #  Get wallet address
#BINANCE_API_URL = "https://testnet.binance.vision/sapi/v1/asset/transfer"

# Node.js API endpoint for Flutterwave processing
FLUTTERWAVE_BASE_URL = settings.FLUTTERWAVE_BASE_URL
FLUTTERWAVE_NODE_API = settings.FLUTTERWAVE_NODE_API
FLUTTERWAVE_SECRET_KEY = settings.FLUTTERWAVE_SECRET_KEY

binance_wallet = settings.BINANCE_ADMIN_WALLET
api_key = binance_wallet.get("api_key")
api_secret = binance_wallet.get("api_secret")
wallet_address= binance_wallet.get("wallet_address")



logger = logging.getLogger(__name__)

@api_view(['POST'])
def flutterwave_webhook(request):
    """Handles Flutterwave payment webhook securely."""
    try:
        payload = request.data  # DRF automatically parses JSON
        logger.info(f"Received Webhook Data: {json.dumps(payload, indent=4)}")

        # Verify Flutterwave signature
        signature = request.headers.get("HTTP_VERIF_HASH")  # Correct header key
        secret_key = settings.FLUTTERWAVE_SECRET_KEY  
        
        expected_signature = hmac.new(
            secret_key.encode(), 
            json.dumps(payload, separators=(',', ':')).encode(), 
            hashlib.sha256
        ).hexdigest()

        if signature != expected_signature:
            logger.warning("Invalid webhook signature")
            return Response({"error": "Invalid signature"}, status=403)

        # Extract transaction details
        event = payload.get("event", "")
        payment_status = payload.get("data", {}).get("status", "")
        transaction_id = payload.get("data", {}).get("id", "")
        flutterwave_tx_ref = payload.get("data", {}).get("tx_ref", "")
        amount_received = Decimal(str(payload.get("data", {}).get("amount", "0")))

        if event == "charge.completed" and payment_status == "successful":
            transaction = get_object_or_404(Transaction, reference=flutterwave_tx_ref)

            # Calculate transaction fee (e.g., 4%)
            transaction_fee = amount_received * Decimal("0.04")

            # Update transaction status and store Flutterwave transaction ID
            transaction.status = "successful"
            transaction.flutterwave_tx_id = transaction_id
            transaction.save()

            # Transfer the fee to AdminWallet
            admin_wallet, _ = AdminWallet.objects.get_or_create(name="Binance")
            admin_wallet.balance += transaction_fee
            admin_wallet.save()

            logger.info(f"Transaction {transaction_id} processed successfully. Fee {transaction_fee} sent to AdminWallet.")

            return Response({"message": "Payment verified, fee deducted, and sent to AdminWallet"}, status=200)

        logger.warning(f"Unhandled event type: {event}")
        return Response({"message": "Webhook received, but no action taken"}, status=200)

    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}", exc_info=True)
        return Response({"error": str(e)}, status=400)
        return JsonResponse({"error": "Internal Server Error", "details": str(e)}, status=500)


@api_view(['POST'])
def payment_webhook(request):
    """Handles generic payment provider webhook securely."""
    try:
        data = request.data  # DRF automatically parses JSON
        transaction_ref = data.get("transaction_reference")
        status = data.get("status")

        if not transaction_ref or not status:
            return Response({"error": "Missing required fields"}, status=400)

        transaction = get_object_or_404(Transaction, reference=transaction_ref)
        transaction.status = status
        transaction.save()

        logger.info(f"Transaction {transaction_ref} updated to status {status}.")
        return Response({"message": "Transaction updated successfully"}, status=200)

    except json.JSONDecodeError:
        return Response({"error": "Invalid JSON payload"}, status=400)
    except Exception as e:
        logger.error(f"Error processing generic webhook: {str(e)}", exc_info=True)
        return Response({"error": str(e)}, status=400)




@csrf_exempt
@require_POST  # Ensures only POST requests are accepted
def payment_callback(request):
    try:
        response_data = json.loads(request.body)
        transaction_ref = response_data.get("tx_ref")
        status = response_data.get("status")

        if not transaction_ref:
            return JsonResponse({"error": "Missing transaction reference"}, status=400)

        # Validate transaction reference
        transaction = get_object_or_404(Transaction, reference=transaction_ref)  

        if status == "successful":
            transaction.status = "Completed"
            transaction.save()
            process_transaction_fee(transaction.transaction_fee, transaction.currency)
            logger.info(f"Transaction {transaction_ref} marked as Completed.")
            return JsonResponse({"message": "Payment successful"}, status=200)
        elif status in ["failed", "cancelled"]:
            transaction.status = "Failed"
            transaction.save()
            logger.warning(f"Transaction {transaction_ref} failed or cancelled.")
            return JsonResponse({"error": "Payment failed or cancelled"}, status=400)
        else:
            return JsonResponse({"error": "Unknown payment status"}, status=400)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON payload"}, status=400)
    except Exception as e:
        logger.error(f"Payment callback error: {str(e)}", exc_info=True)


@api_view(["POST"])
def update_transaction(request):
    #  Secure API Key Verification
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return Response({"error": "Missing or invalid Authorization header"}, status=status.HTTP_401_UNAUTHORIZED)

    api_key = auth_header.replace("Bearer ", "").strip()
    if api_key != settings.DJANGO_API_SECRET_KEY:
        return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

    #  Process Transaction Update
    data = request.data
    tx_ref = data.get("tx_ref")
    status_value = data.get("status")

    if not tx_ref or not status_value:
        return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        transaction = Transaction.objects.get(tx_ref=tx_ref)
        transaction.status = status_value
        transaction.save()
        return Response({"message": "Transaction updated successfully"}, status=status.HTTP_200_OK)

    except Transaction.DoesNotExist:
        return Response({"error": "Transaction not found"}, status=status.HTTP_404_NOT_FOUND)



@api_view(["POST"])
def process_payment_request(request):
    """API endpoint to handle payment requests"""
    logger.debug(f"Received Payment Request: {request.data}")

    transaction_id = request.data.get("transaction_id")
    payment_method = request.data.get("payment_method")
    amount = request.data.get("amount")
    currency = request.data.get("currency")
    recipient = request.data.get("recipient")

    if not all([transaction_id, payment_method, amount, currency, recipient]):
        logger.warning("Missing required fields in request")
        return Response({"error": "Missing required fields"}, status=400)

    # Process the payment via Flutterwave API
    payment_response = process_flutterwave_payment(amount, currency, payment_method)

    if "error" in payment_response:
        return Response({"error": "Payment processing failed"}, status=500)

    return Response({"success": "Payment initiated", "data": payment_response}, status=200)


# Node.js API endpoint for Flutterwave processing
FLUTTERWAVE_BASE_URL = settings.FLUTTERWAVE_BASE_URL
FLUTTERWAVE_NODE_API = settings.FLUTTERWAVE_NODE_API
FLUTTERWAVE_SECRET_KEY = settings.FLUTTERWAVE_SECRET_KEY

print("Using API Key:", FLUTTERWAVE_SECRET_KEY)
print('using node url', FLUTTERWAVE_NODE_API)
print('BINANCE_API_URL', BINANCE_API_URL)

logger = logging.getLogger(__name__)

@csrf_exempt  
def initiate_flutterwave_payment(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        data = json.loads(request.body)

        # Validate required fields
        required_fields = ["amount", "currency", "recipient", "payment_method"]
        if not all(field in data for field in required_fields):
            return JsonResponse({"error": "Missing required fields"}, status=400)

        payment_method = data.get("payment_method", "").strip()
        country = data.get("country", "").strip()
        if not payment_method or not country:
            return JsonResponse({"error": "Payment method and country are required"}, status=400)

        amount = Decimal(str(data["amount"]))
        recipient = get_object_or_404(Recipient, id=data["recipient"])
        phone_number = data.get("phone_number", recipient.phone_number)
        email = request.user.email if request.user.is_authenticated else "worldttance@gmail.com"

        if payment_method in ["m-pesa", "mobile_wallet"] and not phone_number:
            return JsonResponse({"error": "Phone number is required for M-Pesa and Mobile Wallet payments"}, status=400)

        # Generate a unique transaction reference
        tx_ref = f"WT_{uuid.uuid4().hex[:8]}"  

        # Create transaction record
        transaction = Transaction.objects.create(
            user=request.user if request.user.is_authenticated else None,
            recipient=recipient,
            amount=amount,
            currency=data["currency"],
            status="Pending",
            transaction_reference=tx_ref,  # Store transaction reference
        )

        # Prepare payment data
        payment_data = {
            "tx_ref": tx_ref,
            "amount": float(amount),
            "currency": data["currency"],
            "payment_options": payment_method,
            "customer": {
                "email": email,
                "name": request.user.get_full_name() if request.user.is_authenticated else "Test User"
            },
            "redirect_url": "https://1283-105-161-18-79.ngrok-free.app/WorldTtance/api/flutterwave/payment_callback/",
        }

        # Include Google Pay or Apple Pay token if provided
        for token in ["google_pay_token", "apple_pay_token"]:
            if token in data:
                payment_data[token] = data[token]

        # Handle Card Payments (Visa, Mastercard, Amex)
        if payment_method in ["visa", "mastercard", "american_express"]:
            required_card_fields = ["card_number", "cvv", "expiry_month", "expiry_year"]
            missing_fields = [field for field in required_card_fields if field not in data or not data[field]]

            if missing_fields:
                return JsonResponse({"error": f"Missing card details: {', '.join(missing_fields)}"}, status=400)

            payment_data["card_details"] = {
                "card_number": data["card_number"],
                "cvv": data["cvv"],
                "expiry_month": data["expiry_month"],
                "expiry_year": data["expiry_year"],
            }

        # Handle Bank Transfer Payments
        if payment_method == "bank_transfer":
            payment_data["bank_details"] = {
                "account_number": data.get("account_number"),
                "bank_name": data.get("bank_name"),
                "account_name": data.get("account_name"),
                "routing_number": data.get("routing_number"),
                "swift_code": data.get("swift_code"),
            }

        # Send data to Flutterwave API
        headers = {
            "Authorization": f"Bearer {settings.FLUTTERWAVE_SECRET_KEY}",
            "Content-Type": "application/json"
        }

        response = requests.post("https://api.flutterwave.com/v3/payments", json=payment_data, headers=headers)

        try:
            response_data = response.json()
        except json.JSONDecodeError:
            return JsonResponse({
                "error": "Unexpected response from API (not JSON)",
                "details": response.text
            }, status=500)

        # If Flutterwave API call is successful
        if response.status_code == 200 and response_data.get("status") == "success":
            transaction.status = "Initiated"
            transaction.save()
            return JsonResponse({"payment_link": response_data["data"].get("link", "")})

        return JsonResponse({"error": "Flutterwave API error", "details": response.text}, status=500)

    except (json.JSONDecodeError, ValueError):
        return JsonResponse({"error": "Invalid JSON payload"}, status=400)

    except Exception as e:
        logger.exception("Unexpected error during payment initiation")
        return JsonResponse({"error": "Internal Server Error", "details": str(e)}, status=500)

def check_transaction_status(transaction_id):
    url = f"https://api.flutterwave.com/v3/transactions/{transaction_id}/verify"
    headers = {
        "Authorization": f"Bearer {settings.FLUTTERWAVE_SECRET_KEY}",
        "Content-Type": "application/json",
    }
    
    response = requests.get(url, headers=headers)
    return response.json()





# Setup logging
logger = logging.getLogger(__name__)


@csrf_exempt
def verify_payment(request):
    """Verifies a payment with Flutterwave and updates the transaction status."""
    
    if request.method != "GET":
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)

    try:
        # Step 1: Extract transaction reference from request
        flutterwave_tx_id = request.GET.get("transaction_id")
        if not flutterwave_tx_id:
            logger.error("Transaction ID missing in request.")
            return JsonResponse({"status": "error", "message": "Missing transaction ID"}, status=400)

        # Step 2: Call Flutterwave API for verification
        headers = {
            "Authorization": f"Bearer {settings.FLUTTERWAVE_SECRET_KEY}",
            "Content-Type": "application/json",
        }
        verification_url = f"https://api.flutterwave.com/v3/transactions/{flutterwave_tx_id}/verify"
        response = requests.get(verification_url, headers=headers)
        response_data = response.json()

        logger.info(f"Flutterwave Verification Response: {response_data}")

        # Step 3: Validate Flutterwave response
        if response_data.get("status") == "success":
            payment_data = response_data["data"]
            tx_ref = payment_data.get("tx_ref")  # Get your internal transaction reference

            # Step 4: Fetch transaction from the database using `tx_ref`
            try:
                transaction = Transaction.objects.get(tx_ref=tx_ref)
            except Transaction.DoesNotExist:
                logger.error(f"Transaction with tx_ref {tx_ref} not found.")
                return JsonResponse({"status": "error", "message": "Transaction not found"}, status=404)

            # Step 5: Process payment status
            flutterwave_status = payment_data.get("status")
            if flutterwave_status == "successful":
                transaction.status = "Completed"
                transaction.save()
                return JsonResponse({"status": "success", "message": "Payment successful!"})
            elif flutterwave_status == "pending":
                return JsonResponse({"status": "pending", "message": "Payment is still being processed."})
            else:
                transaction.status = "Failed"
                transaction.save()
                return JsonResponse({"status": "error", "message": "Payment failed. Try again later."}, status=400)

        else:
            logger.error(f"Payment verification failed: {response_data.get('message', 'Unknown error')}")
            return JsonResponse({"status": "error", "message": "Verification failed. Please contact support."}, status=400)

    except Exception as e:
        logger.exception("Unexpected error during payment verification")
        return JsonResponse({"status": "error", "message": "Verification error. Try again later."}, status=500)

