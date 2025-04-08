from django.http import JsonResponse
import requests
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings

import logging
from decimal import Decimal
from WorldTtance.choices import COUNTRIES,CURRENCY_CHOICES,PAYMENT_METHODS
import json
from .flutterwave import flutterwave_payout
import json

from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from WorldTtance.models import Transaction, Recipient, AdminWallet
from WorldTtance.views import recipient_list

# Setup logging
logger = logging.getLogger(__name__)

# Get Flutterwave Secret Key from settings
FLUTTERWAVE_SECRET_KEY = settings.FLUTTERWAVE_SECRET_KEY

@csrf_exempt
def initiate_payment(request):
    """Handles payment initiation via Flutterwave API."""
    
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)

    try:        # Step 1: Parse the request data
        data = json.loads(request.body)
        user = request.user
        recipient_id = data.get("recipient")
        amount = float(data.get("amount", 0))
        country = data.get("country", "Kenya")
        currency = data.get("currency", "USD")
        payment_method = data.get("payment_method", "visa")

        # Step 2: Validate recipient
        try:
            recipient = Recipient.objects.get(id=recipient_id)
        except Recipient.DoesNotExist:
            logger.error(f"Recipient ID {recipient_id} not found.")
            return JsonResponse({"status": "error", "message": "Recipient not found"}, status=404)

        # Step 3: Validate card details for card payments
        if payment_method in ["Visa", "MasterCard", "Amex"]:
            card_number = data.get("card_number", "").strip()
            expiry_date = data.get("expiry_date", "").strip()
            cvv = data.get("cvv", "").strip()

            if not card_number or not expiry_date or not cvv:
                logger.error("Missing card details")
                return JsonResponse({"status": "error", "message": " Please enter valid card details."}, status=400)

            if len(cvv) not in [3, 4]:  # Validate CVV length
                logger.error("Invalid CVV length")
                return JsonResponse({"status": "error", "message": " Invalid CVV."}, status=400)

        # Step 4: Calculate transaction fee and total amount
        exchange_rate = 1.0  # Get exchange rate dynamically if needed
        transaction_fee = amount * 0.04  # Example: 4% fee
        total_amount = amount + transaction_fee

        # Step 5: Fetch AdminWallet for Binance fees
        admin_wallet = AdminWallet.objects.first()

        # Step 6: Save transaction in database
        transaction = Transaction.objects.create(
            user=user,
            recipient=recipient,
            amount=amount,
            country=country,
            currency=currency,
            exchange_rate=exchange_rate,
            transaction_fee=transaction_fee,
            total_amount=total_amount,
            admin_wallet=admin_wallet,
            payment_method=payment_method,
            status="Pending"
        )

        # Step 7: Prepare payload for Flutterwave API
        headers = {
            "Authorization": f"Bearer {FLUTTERWAVE_SECRET_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "tx_ref": f"txn_{transaction.id}",
            "amount": total_amount,
            "currency": currency,
            "redirect_url": "https://1283-105-161-18-79.ngrok-free.app/payments/verify/",
            "customer": {
                "email": user.email,
            },
            "customizations": {
                "title": "WorldTtance Payment",
                "description": "Secure Remittance Payment",
            },
        }

        # Step 8: Send request to Flutterwave API
        response = requests.post("https://api.flutterwave.com/v3/payments", json=payload, headers=headers)
        response_data = response.json()

        # Step 9: Handle Flutterwave response
        logger.info(f"Flutterwave API Response: {response_data}")

        if response_data.get("status") == "success":
            return JsonResponse({"status": "success", "payment_url": response_data["data"]["link"]})
        else:
            error_message = response_data.get("message", " Payment failed: Try again later")
            logger.error(f"Flutterwave Payment Error: {error_message}")
            return JsonResponse({"status": "error", "message": f" {error_message}"}, status=400)

    except Exception as e:
        logger.exception("Unexpected error during payment initiation")
        return JsonResponse({"status": "error", "message": " Payment failed: Try again later"}, status=500)


# Setup logging
logger = logging.getLogger(__name__)

# Get Flutterwave Secret Key from settings
FLUTTERWAVE_SECRET_KEY = settings.FLUTTERWAVE_SECRET_KEY

@csrf_exempt
def verify_payment(request):
    """Verifies a payment with Flutterwave and updates the transaction status."""

    if request.method != "GET":
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)

    try:
        # Step 1: Extract transaction reference from request
        transaction_id = request.GET.get("transaction_id")
        if not transaction_id:
            logger.error("Transaction ID missing in request.")
            return JsonResponse({"status": "error", "message": " Missing transaction ID"}, status=400)

        # Step 2: Fetch transaction from the database
        try:
            transaction = Transaction.objects.get(id=transaction_id)
        except Transaction.DoesNotExist:
            logger.error(f"Transaction with ID {transaction_id} not found.")
            return JsonResponse({"status": "error", "message": " Transaction not found"}, status=404)

        # Step 3: Make request to Flutterwave API for verification
        headers = {
            "Authorization": f"Bearer {FLUTTERWAVE_SECRET_KEY}",
            "Content-Type": "application/json",
        }
        verification_url = f"https://api.flutterwave.com/v3/transactions/{transaction_id}/verify"
        response = requests.get(verification_url, headers=headers)
        response_data = response.json()

        logger.info(f"Flutterwave Verification Response: {response_data}")

        # Step 4: Process response from Flutterwave
        if response_data.get("status") == "success":
            flutterwave_status = response_data["data"]["status"]

            if flutterwave_status == "successful":
                # Step 5: Mark transaction as successful
                transaction.status = "Completed"
                transaction.save()

                return JsonResponse({"status": "success", "message": " Payment successful!"})
            
            elif flutterwave_status == "pending":
                # Payment is still being processed
                return JsonResponse({"status": "pending", "message": "⏳ Payment is still being processed."})

            else:
                # Payment failed
                transaction.status = "Failed"
                transaction.save()
                return JsonResponse({"status": "error", "message": " Payment failed. Try again later."}, status=400)

        else:
            logger.error(f"Payment verification failed: {response_data.get('message', 'Unknown error')}")
            return JsonResponse({"status": "error", "message": " Verification failed. Please contact support."}, status=400)

    except Exception as e:
        logger.exception("Unexpected error during payment verification")
        return JsonResponse({"status": "error", "message": " Verification error. Try again later."}, status=500)



  # Ensure correct model imports

logger = logging.getLogger(__name__)

binance_wallet = settings.BINANCE_ADMIN_WALLET
api_key = binance_wallet["api_key"]
api_secret = binance_wallet["api_secret"]
wallet_address = binance_wallet["wallet_address"]  #  Get wallet address


def transfer_fees_to_admin(transaction_id):
    try:
        # Retrieve transaction
        transaction = Transaction.objects.get(id=transaction_id)

        if not transaction.transaction_fee or not transaction.currency:
            return {"success": False, "error": "Invalid transaction fee or currency"}

        # Convert fee to proper format
        amount = str(Decimal(transaction.transaction_fee).quantize(Decimal("0.00000001")))
        currency = transaction.currency.upper()

        if not currency:
            return {"success": False, "error": "Currency format is invalid"}

        # Process transaction fee transfer
        return process_transaction_fee(amount, currency)

    except Transaction.DoesNotExist:
        return {"success": False, "error": f"Transaction with ID {transaction_id} not found."}

    except Exception as e:
        logger.critical(f"Transfer Fees to Admin Error: {str(e)}")
        return {"success": False, "error": str(e)}

def process_transaction_fee(amount, currency):
    """
    Transfers collected transaction fees to the Binance Admin Wallet.
    """
    admin_wallet = AdminWallet.objects.first()
    if not admin_wallet:
        return {"success": False, "error": "AdminWallet not found"}

    headers = {"Authorization": f"Bearer {api_key}"}
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
        
@csrf_exempt
def process_payout(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            amount = data.get("amount")
            recipient_account = data.get("account_number")
            recipient_name = data.get("recipient_name")
            recipient_bank = data.get("bank_code")
            currency = data.get("currency", "NGN")

            response = flutterwave_payout(amount, recipient_account, recipient_name, recipient_bank, currency)
            return JsonResponse(response)

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    
    return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)


@login_required
def payment_page(request, payment_method="default"):  # Set a default value
    recipients = Recipient.objects.filter(user=request.user)  

    context = {
        "recipients": recipient_list,
        "currencies": CURRENCY_CHOICES,
        "payment_methods": PAYMENT_METHODS,
        "countries": COUNTRIES,
        "selected_payment_method": payment_method,
    }
    return render(request, "payments/payments.html", context)



@login_required
def some_payment_selection_view(request):
    context = {
        "payment_methods": PAYMENT_METHODS,  # Ensure this variable is defined in your settings or models
    }
    return render(request, "payments/choose_payment.html", context)



@login_required
def payment_failed(request):
    error_message = request.GET.get('error', 'An unknown error occurred during payment.')
    return render(request, 'payments/payment_failed.html', {'error_message': error_message})
    


FLW_SECRET_KEY = settings.FLUTTERWAVE_SECRET_KEY  # Ensure this is set in settings.py

def process_payments(request):
    if request.method == "POST":
        payment_method = request.POST.get("payment_method")
        amount = request.POST.get("amount")
        currency = request.POST.get("currency")
        recipient_id = request.POST.get("recipient")

        payload = {
            "tx_ref": "worldttance_" + str(request.user.id),
            "amount": amount,
            "currency": currency,
            "redirect_url": request.build_absolute_uri("/payment-success/"),
            "payment_options": "card",
            "customer": {
                "email": request.user.email,
                "phonenumber": "1234567890",
                "name": request.user.get_full_name(),
            },
            "customizations": {
                "title": "WorldTtance Payment",
                "description": "Send Money Securely",
                "logo": "https://1283-105-161-18-79.ngrok-free.app//static/logo.png",
            },
        }

        headers = {
            "Authorization": f"Bearer {FLW_SECRET_KEY}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(
                "https://api.flutterwave.com/v3/payments",
                headers=headers,
                json=payload,
            )
            response_data = response.json()

            print("FLW Response:", json.dumps(response_data, indent=2))  # Debugging

            if response_data.get("status") == "success":
                return redirect(response_data["data"]["link"])
            else:
                messages.error(request, response_data.get("message", " Payment failed."))
                return redirect("payment_failed")

        except requests.exceptions.RequestException as e:
            print("FLW API Error:", str(e))  # Debugging
            messages.error(request, " Unable to process payment. Please try again later.")
            return redirect("payment_failed")

    return redirect("choose_payment_method")
