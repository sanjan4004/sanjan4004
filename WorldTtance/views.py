from django.contrib.auth.models import User
from .models import Recipient, Transaction,UserProfile,KYCVerification,AdminWallet
from django.http import HttpResponse
from .forms import RecipientForm, TransactionForm,KYCVerificationForm,UserProfileForm, UserUpdateForm,UserRegisterForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
import json
from django.http import JsonResponse
from .choices import PAYMENT_METHODS, COUNTRIES,CURRENCY_CHOICES,CRYPTO_CHOICES
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from .utils import send_transaction_email,transfer_fees_to_admin,send_bitcoin_payment,process_transaction_fee,generate_binance_signature,send_binance_payment,convert_currency_to_crypto,transfer_fees_to_admin
from django.conf import settings
from decimal import Decimal
from django.urls import reverse
import uuid
from django.core.files.base import ContentFile
from binance.client import Client
from binance.exceptions import BinanceAPIException
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import logging
import requests 
import os
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view
from rest_framework.response import Response
import hmac
import hashlib
from rest_framework import generics
from .serializers import AdminWalletSerializer  #  Correct relative import
from rest_framework.permissions import IsAdminUser
from django.core.paginator import Paginator
from rest_framework.views import APIView
from rest_framework import status
from .serializers import RecipientSerializer
from rest_framework.permissions import IsAuthenticated
from django.template.loader import get_template
from django.http import HttpResponseNotFound
from django.db import transaction as db_transaction
import time
import random
from .utils import send_transaction_to_node,get_exchange_rate # Ensure this function exists



# USER SEESIONS
def store_session_data(request):
    request.session["transaction_id"] = "TXN123456"
    return HttpResponse("Session data saved!")

def retrieve_session_data(request):
    transaction_id = request.session.get("transaction_id", "No transaction found")
    return HttpResponse(f"Transaction ID: {transaction_id}")

def clear_session_data(request):
    request.session.flush()  # Clears all session data
    return HttpResponse("Session cleared!")
@csrf_exempt
def homepage(request):
    """Render the homepage."""
    return render(request, 'home.html')


#TO CALCULATE EXCHANGE RATES 
def calculate_converted_amount(base_currency, target_currency, amount):
    rate = get_exchange_rate(base_currency, target_currency)
    return amount * rate



@login_required
def dashboard(request):
    # Fetch user's transaction history
    transactions = Transaction.objects.filter(user=request.user).order_by('-timestamp')

    # Paginate transactions (reuse logic from transaction history)
    paginator = Paginator(transactions, 10)  # Show 10 transactions per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'recent_transactions': page_obj,  # Passed for dashboard transaction list
        'user_profile': request.user.profile if hasattr(request.user, 'profile') else None,
    }
    return render(request, 'dashboard.html', context)




@login_required
def new_recipient(request):
    try:
        get_template("recipients/recipient_form.html")  # Check if Django finds the template
        print(" Template found!")
    except:
        print("Template NOT found!")
        return HttpResponseNotFound("Template NOT found!")

    form = RecipientForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        recipient = form.save(commit=False)
        recipient.user = request.user
        recipient.save()
        return redirect('recipient_list')

    return render(request, 'recipients/recipient_form.html', {'form': form})




@login_required
def recipient_edit(request, pk):
    recipient = get_object_or_404(Recipient, pk=pk, user=request.user)
    
    if request.method == "POST":
        form = RecipientForm(request.POST, instance=recipient)
        if form.is_valid():
            form.save()
            return redirect('recipient_list')
    else:
        form = RecipientForm(instance=recipient)

    return render(request, 'recipients/recipient_edit.html', {'form': form, 'recipient': recipient})




def recipient_form_view(request):
    return render(request, "recipients/recipient_form.html")  #  This will work if placed correctly


def new_transaction_form_view(request):
    return render(request, "transactions/transaction_form.html")  #  This will work if placed correctly


@login_required
def recipient_list(request):
    recipients = Recipient.objects.filter(user=request.user)
    return render(request, 'recipients/recipient_list.html', {'recipients': recipients})



@login_required
def recipient_delete(request, recipient_id):
    recipient = get_object_or_404(Recipient, id=recipient_id, user=request.user)

    if request.method == "POST":
        recipient.delete()
        messages.success(request, "Recipient deleted successfully!")
        return redirect("recipient_list")

    return render(request, "recipients/recipient_confirm_delete.html", {"recipient": recipient})



def custom_login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({"error": "Authentication required"}, status=401)
            return login_required(view_func)(request, *args, **kwargs)
        return view_func(request, *args, **kwargs)
    return wrapper



logger = logging.getLogger(__name__)

def _handle_error_response(is_ajax, error_msg, redirect_page, request):
    if is_ajax:
        return JsonResponse({"error": error_msg}, status=400)
    messages.error(request, error_msg)
    return redirect(redirect_page)

def _handle_redirect(is_success, success_msg, error_msg, request):
    if is_success:
        messages.success(request, success_msg)
        return redirect("transaction_success")
    else:
        messages.error(request, error_msg)
        return redirect("transaction_history")


@login_required
def new_transaction(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    success_msg = ""

    if request.method == "POST":
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.transaction_fee = transaction.amount * Decimal("0.04")

            # Ensure the amount is enough for fee deduction
            if transaction.amount - transaction.transaction_fee < Decimal("1.00"):
                error_msg = "Transaction amount is too low after fee deduction."
                return JsonResponse({"error": error_msg}, status=400)

            try:
                with db_transaction.atomic():
                    transaction.transaction_reference = generate_transaction_reference()  #  Fix: Generate transaction ref
                    transaction.amount -= transaction.transaction_fee
                    transaction.status = "Pending"
                    transaction.save()

                    response = send_transaction_to_node(transaction)

                    if not response or response.get("status") != "success":
                        raise ValueError(f"Transaction failed: {response.get('message', 'Unknown error')}")

                    transaction.status = "Completed"
                    success_msg = "Transaction created successfully!"
                    transaction.save()

            except Exception as e:
                transaction.status = "Failed"
                transaction.save()
                error_msg = f"Transaction processing failed: {str(e)}"
                return JsonResponse({"error": error_msg}, status=400)

            if is_ajax:
                return JsonResponse({"message": success_msg, "transaction_id": transaction.id}, status=200)

            return _handle_redirect(transaction.status == "Completed", success_msg, error_msg, request)

    else:
        form = TransactionForm()

    if is_ajax:
        return JsonResponse({"error": "GET method is not allowed"}, status=405)

    return render(request, "transactions/transaction_form.html", {"form": form})


@login_required
def transaction_history(request):
    transactions = Transaction.objects.filter(user=request.user).order_by('-timestamp')

    paginator = Paginator(transactions, 10)  # Paginate the transactions, 10 per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'recent_transactions': page_obj  # Change 'transactions' to 'recent_transactions' to match template
    }
    return render(request, 'transactions/transaction_history.html', context)


@csrf_exempt
def transaction_success(request):
    tx_ref = request.GET.get("tx_ref")

    if not tx_ref:
        return render(request, "transactions/transaction_success.html", {"error": "No transaction reference provided."})

    transaction = get_object_or_404(Transaction, transaction_reference=tx_ref)

    return render(request, "transactions/transaction_success.html", {"transaction": transaction})

@csrf_exempt
def transaction_failed(request):
    tx_ref = request.GET.get("tx_ref")
    transaction = None
    error_message = "Transaction failed or was cancelled."

    if tx_ref:
        try:
            transaction = Transaction.objects.get(transaction_reference=tx_ref)
        except Transaction.DoesNotExist:
            error_message = f"No transaction found for reference: {tx_ref}"

    context = {
        "tx_ref": tx_ref,
        "transaction": transaction,
        "error_message": error_message,
    }
    return render(request, "transactions/transaction_failed.html", context)



@login_required
def profile_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    return render(request, "account/user_profile.html", {"profile": profile})

@login_required
def edit_profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            return redirect("profile_view")
    else:
        form = UserProfileForm(instance=profile)

    return render(request, "account/edit_profile.html", {"form": form})


@login_required
def kyc_verification(request):
    try:
        kyc = KYCVerification.objects.get(user=request.user)
    except KYCVerification.DoesNotExist:
        kyc = None

    if request.method == 'POST':
        form = KYCVerificationForm(request.POST, request.FILES, instance=kyc)
        if form.is_valid():
            kyc = form.save(commit=False)
            kyc.user = request.user
            kyc.status = 'Pending'
            kyc.save()
            return redirect('kyc_status')
    else:
        form = KYCVerificationForm(instance=kyc)

    return render(request, 'kyc/kyc_verification.html', {'form': form})


@login_required
def kyc_capture(request):
    if request.method == "POST":
        image_data = request.POST.get("image_data")
        if image_data:
            # Remove Base64 header
            format, imgstr = image_data.split(";base64,")
            ext = format.split("/")[-1]

            # Generate unique filename
            image_name = f"kyc_{uuid.uuid4()}.{ext}"

            # Convert Base64 to Django ImageFile
            image_file = ContentFile(base64.b64decode(imgstr), name=image_name)

            # Save KYC data to the database
            kyc_entry = KYCVerification(user=request.user, document_image=image_file)
            kyc_entry.save()

            messages.success(request, "KYC submitted successfully!")
            return redirect("kyc_success")

    return render(request, "kyc/kyc_camera.html")



@login_required
def kyc_status(request):
    kyc = KYCVerification.objects.filter(user=request.user).first()
    return render(request, 'kyc/kyc_status.html', {'kyc': kyc})
        
#Email Notification for a complete transaction

@login_required
def complete_transaction(request, transaction_id):
    transaction = Transaction.objects.get(id=transaction_id)
    user = transaction.user

    # Send Transaction Email
    subject = "Transaction Completed - WorldTtance"
    html_message = render_to_string("email_templates/transaction_completed.html", {
        "user": user,
        "amount": transaction.amount,
        "currency": transaction.currency,
        "recipient_name": transaction.recipient.full_name,
        "transaction_id": transaction.id
    })
    plain_message = strip_tags(html_message)
    send_mail(subject, plain_message, "no-reply@worldttance.com", [user.email], html_message=html_message)

    return redirect("transaction_history")





@login_required
def start_binance_transaction_check(request, transaction_id):
    check_binance_transaction.delay(transaction_id)
    return JsonResponse({"message": f"Transaction check started for {transaction_id}"})


class AdminWalletUpdateView(generics.UpdateAPIView):
    queryset = AdminWallet.objects.all()
    serializer_class = AdminWalletSerializer
    permission_classes = [IsAdminUser]
    http_method_names = ['get', 'patch', 'put']  # Ensure PATCH is allowed



class UpdateAdminWalletView(APIView):
    def put(self, request, *args, **kwargs):
        wallet = AdminWallet.objects.first()
        if not wallet:
            return Response({"error": "Admin wallet not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = AdminWalletSerializer(wallet, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RecipientListCreateView(generics.ListCreateAPIView):
    """
    API view to list and create recipients.
    """
    queryset = Recipient.objects.all()
    serializer_class = RecipientSerializer
    permission_classes = [IsAuthenticated]  # Ensure authentication is required

    def get_queryset(self):
        return Recipient.objects.filter(user=self.request.user)  # Show only user's recipients



# Initialize Binance client
BINANCE_API_URL = settings.BINANCE_API_BASE_URL
binance_wallet = settings.BINANCE_ADMIN_WALLET
api_key = binance_wallet["api_key"]
api_secret = binance_wallet["api_secret"]
wallet_address = binance_wallet["wallet_address"]  #  Get wallet address
#BINANCE_API_URL = "https://testnet.binance.vision/sapi/v1/asset/transfer"



from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException
# Logger for Debugging
logger = logging.getLogger(__name__)
# Binance API Client (Use Environment Variables in Production)
binance_client = Client(api_key=api_key, api_secret= api_secret)

@csrf_exempt
def process_binance_payment(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        # Parse JSON Data
        data = json.loads(request.body)
        amount = data.get("amount")
        currency = data.get("currency")
        recipient_wallet = data.get("recipient_wallet")

        # Validate Required Fields
        if not all([amount, currency, recipient_wallet]):
            logger.critical("Missing required fields in Binance payment request: %s", data)
            return JsonResponse({"error": "Missing required fields"}, status=400)

        try:
            amount = Decimal(str(amount))  # Convert amount to Decimal
            if amount <= 0:
                return JsonResponse({"error": "Invalid transaction amount"}, status=400)
        except:
            return JsonResponse({"error": "Invalid amount format"}, status=400)

        currency = currency.upper()  # Binance uses uppercase symbols like "USDT"

        # **Save Transaction to Database Before Processing**
        transaction = Transaction.objects.create(
            user=request.user if request.user.is_authenticated else None,
            recipient_wallet=recipient_wallet,
            amount=amount,
            currency=currency,
            status="Pending",
            payment_method="binance",
        )

        # **Send payment via Binance API**
        logger.info(f"Initiating Binance transfer: {amount} {currency} to {recipient_wallet}")

        response = binance_client.withdraw(
            asset=currency,
            address=recipient_wallet,
            amount=str(amount)  # Binance API requires a string
        )

        # **Save Success Response in DB**
        transaction.status = "Completed"
        transaction.transaction_id = response.get("id", "N/A")
        transaction.save()

        logger.info(f"Binance Payment Successful. Transaction ID: {response.get('id', 'N/A')}")
        return JsonResponse({"message": "Payment successful", "transaction_id": response.get("id")})

    except (BinanceAPIException, BinanceRequestException, BinanceWithdrawException) as e:
        logger.critical(f"Binance API Error: {e.message}")
        transaction.status = "Failed"
        transaction.error_message = e.message
        transaction.save()
        return JsonResponse({"error": f"Binance API Error: {e.message}"}, status=500)

    except json.JSONDecodeError:
        logger.critical(f"Invalid JSON format received: {request.body}")
        return JsonResponse({"error": "Invalid JSON format"}, status=400)

    except Exception as e:
        logger.critical(f"Unexpected Error in Binance Payment Processing: {str(e)}", exc_info=True)
        transaction.status = "Failed"
        transaction.error_message = str(e)
        transaction.save()
        return JsonResponse({"error": "Internal Server Error"}, status=500)



# Node.js API endpoint for Flutterwave processing
FLUTTERWAVE_BASE_URL = settings.FLUTTERWAVE_BASE_URL
FLUTTERWAVE_NODE_API = settings.FLUTTERWAVE_NODE_API
FLUTTERWAVE_SECRET_KEY = settings.FLUTTERWAVE_SECRET_KEY

print("Using API Key:", FLUTTERWAVE_SECRET_KEY)
print('using node url', FLUTTERWAVE_NODE_API)
print('BINANCE_API_URL', BINANCE_API_URL)

logger = logging.getLogger(__name__)

# ... (your import statements remain unchanged)
import uuid

@csrf_exempt
def initiate_flutterwave_payment(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        data = json.loads(request.body)

        required_fields = ["amount", "currency", "recipient", "payment_method"]
        if not all(field in data for field in required_fields):
            return JsonResponse({"error": "Missing required fields"}, status=400)

        payment_method = data.get("payment_method", "").strip().lower()
        country = data.get("country", "").strip()
        amount = Decimal(str(data["amount"]))
        recipient = get_object_or_404(Recipient, id=data["recipient"])
        phone_number = data.get("phone_number", recipient.phone_number)
        email = request.user.email if request.user.is_authenticated else "worldttance@gmail.com"

        if payment_method in ["m-pesa", "mobile_wallet"] and not phone_number:
            return JsonResponse({"error": "Phone number is required for M-Pesa and Mobile Wallet payments"}, status=400)

        tx_ref = f"WT_{uuid.uuid4().hex[:8]}"

        transaction = Transaction.objects.create(
            user=request.user if request.user.is_authenticated else None,
            recipient=recipient,
            amount=amount,
            currency=data["currency"],
            status="Pending",
            transaction_reference=tx_ref,
        )

        admin_wallet = AdminWallet.objects.first()
        if admin_wallet:
            transaction_fee = admin_wallet.transaction_fee
            fee_deducted_amount = amount - transaction_fee
            admin_wallet.balance -= transaction_fee
            admin_wallet.save()
            transaction.amount = fee_deducted_amount
            transaction.save()
        else:
            return JsonResponse({"error": "Admin Wallet not found"}, status=500)

        # All amounts as Decimal and converted to string to preserve precision when passing to Node.js
        payment_data = {
            "tx_ref": tx_ref,
            "amount": str(fee_deducted_amount),
            "currency": data["currency"],
            "payment_options": payment_method,
            "customer": {
                "email": email,
                "name": request.user.get_full_name() if request.user.is_authenticated else "Test User"
            },
            "redirect_url": settings.FLUTTERWAVE_REDIRECT_URL,
        }

        for token in ["google_pay_token", "apple_pay_token"]:
            if token in data:
                payment_data[token] = data[token]

        if payment_method in ["visa", "mastercard", "american_express"]:
            missing_fields = [field for field in ["card_number", "cvv", "expiry_month", "expiry_year"]
                              if field not in data or not data[field]]
            if missing_fields:
                return JsonResponse({"error": f"Missing card details: {', '.join(missing_fields)}"}, status=400)

            payment_data["card_details"] = {
                "card_number": data["card_number"],
                "cvv": data["cvv"],
                "expiry_month": data["expiry_month"],
                "expiry_year": data["expiry_year"],
            }

        if payment_method == "bank_transfer":
            payment_data["bank_details"] = {
                "account_number": data.get("account_number"),
                "bank_name": data.get("bank_name"),
                "account_name": data.get("account_name"),
                "routing_number": data.get("routing_number"),
            }

        if payment_method in ["m-pesa", "mobile_wallet"]:
            payment_data["mobile_money"] = {
                "phone_number": phone_number,
                "provider": "mpesa" if payment_method == "m-pesa" else "mobilemoney",
                "country": country or "KE"
            }

        #  Forward to Node.js backend (decimals as strings)
        try:
            response = requests.post(
                f"{settings.FLUTTERWAVE_NODE_API}/flutterwave/initiate",
                json=payment_data,
                timeout=10
            )

            response_data = response.json()
        except requests.RequestException as req_error:
            logger.error(f"Error connecting to Node.js Flutterwave backend: {req_error}")
            return JsonResponse({"error": "Payment gateway timeout"}, status=504)
        except json.JSONDecodeError:
            return JsonResponse({
                "error": "Invalid JSON response from payment gateway",
                "details": response.text
            }, status=500)

        if response.status_code == 200 and response_data.get("status") == "success":
            transaction.status = "Initiated"
            transaction.save()
            return JsonResponse({"payment_link": response_data["data"].get("link", "")})

        return JsonResponse({"error": "Flutterwave API error", "details": response_data}, status=500)

    except (json.JSONDecodeError, ValueError):
        return JsonResponse({"error": "Invalid JSON payload"}, status=400)
    except Exception as e:
        logger.exception("Unexpected error during payment initiation")
        return JsonResponse({"error": "Internal Server Error", "details": str(e)}, status=500)


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


def payment_status(request):
    """
    Handles Flutterwave's redirect after payment.
    Verifies the payment and updates the transaction status.
    """
    status = request.GET.get("status")
    transaction_id = request.GET.get("transaction_id")

    if not transaction_id:
        return JsonResponse({"error": "Transaction ID is missing"}, status=400)

    verify_url = f"https://api.flutterwave.com/v3/transactions/{transaction_id}/verify"
    headers = {"Authorization": f"Bearer {settings.FLUTTERWAVE_SECRET_KEY}"}

    try:
        response = requests.get(verify_url, headers=headers)
        response.raise_for_status()  # Raises an error for non-200 responses
        data = response.json()
    except requests.RequestException as e:
        return JsonResponse({"error": "Failed to verify transaction", "details": str(e)}, status=500)

    if data.get("status") == "success" and data.get("data", {}).get("status") == "successful":
        tx_ref = data["data"].get("tx_ref")
        transaction = get_object_or_404(Transaction, reference=tx_ref)
        transaction.status = "successful"
        transaction.save()

        return HttpResponseRedirect("https://952b-197-232-62-231.ngrok-free.app/WorldTtance/payment-success")

    else:
        tx_ref = data.get("data", {}).get("tx_ref")
        if tx_ref:
            transaction = get_object_or_404(Transaction, reference=tx_ref)
            transaction.status = "failed"
            transaction.save()

        return HttpResponseRedirect("https://952b-197-232-62-231.ngrok-free.app/WorldTtance/payment-failed")



# Node.js API endpoint for Flutterwave processing
FLUTTERWAVE_BASE_URL = settings.FLUTTERWAVE_BASE_URL
binance_wallet = settings.BINANCE_ADMIN_WALLET
api_key = binance_wallet.get("api_key")
api_secret = binance_wallet.get("api_secret")
wallet_address= binance_wallet.get("wallet_address")


import requests
logger = logging.getLogger(__name__)
def process_payment(amount, currency, payment_type, recipient, phone_number=None):
    """ 
    Sends a payment request to the Flutterwave API for various payment methods.
    
    :param amount: Payment amount
    :param currency: Transaction currency (USD, KES, NGN, etc.)
    :param payment_type: Type of payment (card, mpesa, mobilemoney, banktransfer, crypto, googlepay, applepay)
    :param recipient: Recipient details (can be email or name)
    :param phone_number: Required for mobile money transactions
    :return: JSON response with payment link or error
    """

    url = settings.FLUTTERWAVE_NODE_API  # Load from settings
    headers = {
        "Authorization": f"Bearer {settings.FLUTTERWAVE_SECRET_KEY}",
        "Content-Type": "application/json",
    }


    if payment_type.lower() not in PAYMENT_METHODS:
        return {"error": f"Unsupported payment method: {payment_type}"}

    payload = {
        "tx_ref": f"WTX-{recipient}-{amount}",  # Unique transaction ID
        "amount": amount,
        "currency": currency,
        "payment_type": PAYMENT_METHODS[payment_type.lower()],
        "customer": {
            "email": f"{recipient}@example.com",
            "name": recipient,
            "phonenumber": phone_number if phone_number else "0000000000",
        },
        "redirect_url": f"{settings.DJANGO_API_URL}/payment-success/",  # Redirect after payment
        "customizations": {
            "title": "WorldTtance Payment",
            "description": f"Payment to {recipient} via {payment_type.capitalize()}",
            "logo": f"{settings.DJANGO_API_URL}/static/logo.png",
        }
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response_data = response.json()
        logger.info(f"Flutterwave Response: {response_data}")

        if response.status_code != 200 or "data" not in response_data:
            return {"error": "Failed to process payment"}

        payment_link = response_data["data"].get("link")
        return {"payment_link": payment_link} if payment_link else {"error": "Payment link not returned"}

    except requests.exceptions.RequestException as e:
        logger.error(f"Error processing payment: {e}")
        return {"error": "Payment request failed"}

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
    payment_response = process_payment(amount, currency, payment_method,recipient)

    if "error" in payment_response:
        return Response({"error": "Payment processing failed"}, status=500)

    return Response({"success": "Payment initiated", "data": payment_response}, status=200)





logger = logging.getLogger(__name__)

@csrf_exempt
def payment_callback(request):
    """Handles Flutterwave payment callbacks, supporting both GET and POST with redirects."""
    try:
        if request.method == "POST":
            response_data = json.loads(request.body)
        else:
            response_data = request.GET

        transaction_ref = response_data.get("tx_ref")
        status = response_data.get("status")
        transaction_id = response_data.get("transaction_id")

        if not transaction_ref or not transaction_id:
            return JsonResponse({"error": "Missing transaction reference or ID"}, status=400)

        # Fetch transaction
        transaction = get_object_or_404(Transaction, transaction_reference=transaction_ref)

        # Verify via Flutterwave
        verification_url = f"https://api.flutterwave.com/v3/transactions/{transaction_id}/verify"
        headers = {"Authorization": f"Bearer {settings.FLUTTERWAVE_SECRET_KEY}"}

        flw_response = requests.get(verification_url, headers=headers)
        flw_data = flw_response.json()

        if flw_data.get("status") == "success" and flw_data["data"]["status"] == "successful":
            transaction.status = "Completed"
            transaction.save()
            #  Redirect to success page
            return redirect("transaction_success")

        elif flw_data.get("status") == "error" or status in ["failed", "cancelled"]:
            transaction.status = "Failed"
            transaction.save()
            #  Redirect to failure page
            return redirect("transaction_failed")

        else:
            return JsonResponse({"error": "Payment status unknown"}, status=400)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON payload"}, status=400)

    except Exception as e:
        logger.error(f"Payment callback error: {str(e)}", exc_info=True)
        return JsonResponse({"error": "Internal Server Error", "details": str(e)}, status=500)


# Setting up a logger for better error tracking and logging
logger = logging.getLogger(__name__)

@csrf_exempt  # Disable CSRF for external webhook requests
@api_view(['POST'])
@permission_classes([AllowAny])  # Allow external services to call this webhook
def flutterwave_webhook(request):
    """Handles Flutterwave payment webhook"""
    try:
        payload = request.data  # DRF automatically parses JSON
        logger.info(" Received Webhook Data: %s", json.dumps(payload, indent=4))

        # Get Flutterwave verification hash (Using HMAC for improved security)
        received_signature = request.headers.get("verif-hash")
        expected_signature = hmac.new(
            bytes(settings.FLUTTERWAVE_SECRET_KEY, "utf-8"),
            msg=json.dumps(payload).encode("utf-8"),
            digestmod=hashlib.sha256
        ).hexdigest()

        if not received_signature or received_signature != expected_signature:
            logger.warning("Invalid signature received: %s", received_signature)
            return Response({"error": "Invalid signature"}, status=403)

        # Extract relevant data from the webhook
        event = payload.get("event", "")
        transaction_data = payload.get("data", {})

        flutterwave_tx_ref = transaction_data.get("tx_ref", "")
        amount_received = float(transaction_data.get("amount", 0))
        payment_status = transaction_data.get("status", "")

        if event == "charge.completed" and payment_status == "successful":
            # Handle charge completed
            return process_payment_successful(flutterwave_tx_ref, amount_received, transaction_data)

        elif event == "charge.failed":
            # Handle charge failed
            return process_payment_failed(flutterwave_tx_ref)

        elif event == "refund.completed":
            # Handle refund completed
            return process_refund(flutterwave_tx_ref, amount_received)

        # If event is not recognized
        logger.info(" Webhook Event Received: %s", event)
        return Response({"message": "Webhook received but event is not processed"}, status=200)

    except Exception as e:
        logger.error(" Webhook Processing Error: %s", str(e))
        return Response({"error": str(e)}, status=400)



def process_payment_successful(tx_ref, amount_received, transaction_data):
    """Process the successful payment and update transaction and admin wallet."""
    try:
        transaction = Transaction.objects.get(reference=tx_ref)

        # Validate received amount matches gross_amount
        if abs(amount_received - transaction.gross_amount) > 1:
            logger.warning("Amount mismatch: Received %.2f, Expected %.2f", amount_received, transaction.gross_amount)

        # Calculate net amount after fee
        net_amount = amount_received - transaction.transaction_fee
        if net_amount < 0:
            logger.error("Transaction fee exceeds received amount for %s", tx_ref)
            return Response({"error": "Invalid fee configuration"}, status=400)

        # Update transaction details
        transaction.amount = net_amount
        transaction.status = "successful"
        transaction.flutterwave_tx_id = transaction_data.get("id", "")
        transaction.save()

        # Credit fee to AdminWallet
        admin_wallet = transaction.admin_wallet  # Already linked
        admin_wallet.balance += transaction.transaction_fee
        admin_wallet.save()

        logger.info("Payment Verified: %s | Net: %.2f | Fee: %.2f sent to AdminWallet",
                    tx_ref, net_amount, transaction.transaction_fee)
        return Response({"message": "Payment verified, fee transferred to AdminWallet"}, status=200)

    except Transaction.DoesNotExist:
        logger.warning("Transaction Not Found: %s", tx_ref)
        return Response({"error": "Transaction not found"}, status=404)

    except Exception as e:
        logger.error("Error processing payment: %s", str(e))
        return Response({"error": "Error processing payment"}, status=500)



def process_payment_failed(tx_ref):
    """Handle failed payment event."""
    try:
        # Retrieve the transaction and mark it as failed
        transaction = Transaction.objects.get(reference=tx_ref)
        transaction.status = "failed"
        transaction.save()

        logger.info("Payment Failed: %s", tx_ref)
        return Response({"message": "Payment failed"}, status=200)

    except Transaction.DoesNotExist:
        logger.warning(" Transaction Not Found: %s", tx_ref)
        return Response({"error": "Transaction not found"}, status=404)


def process_refund(tx_ref, amount_refunded):
    """Handle refund completed event."""
    try:
        # Retrieve the transaction and update it
        transaction = Transaction.objects.get(reference=tx_ref)

        # Deduct refund amount from AdminWallet (Refund back to wallet)
        admin_wallet, _ = AdminWallet.objects.get_or_create(name="Binance")
        admin_wallet.balance -= amount_refunded
        admin_wallet.save()

        transaction.status = "refunded"
        transaction.amount = 0  # Assuming refund clears the transaction amount
        transaction.save()

        logger.info("Refund Processed: %s | Amount Refunded: %.2f KES", tx_ref, amount_refunded)
        return Response({"message": "Refund processed successfully"}, status=200)

    except Transaction.DoesNotExist:
        logger.warning(" Transaction Not Found: %s", tx_ref)
        return Response({"error": "Transaction not found"}, status=404)
    except Exception as e:
        logger.error(" Error processing refund: %s", str(e))
        return Response({"error": "Error processing refund"}, status=500)


def check_transaction_status(transaction_id):
    url = f"https://api.flutterwave.com/v3/transactions/{transaction_id}/verify"
    headers = {
        "Authorization": f"Bearer {settings.FLUTTERWAVE_SECRET_KEY}",
        "Content-Type": "application/json",
    }
    
    response = requests.get(url, headers=headers)
    return response.json()




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




def process_transaction(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id)

    if transaction.status in ["Completed", "Failed"]:
        return JsonResponse({"message": "Transaction already processed"}, status=400)

    # Get admin wallet
    admin_wallet = AdminWallet.objects.first()

    if not admin_wallet:
        return JsonResponse({"error": "No AdminWallet found"}, status=500)

    # Deduct fee and send to Binance AdminWallet
    fee_amount = transaction.transaction_fee
    binance_wallet = admin_wallet.wallet_address

    success = process_transaction_fee(fee_amount, binance_wallet) #transfer_fees_to_binance

    if success:
        admin_wallet.deposit_fee(fee_amount)
        transaction.status = "Completed"
        transaction.save()
        return JsonResponse({"message": "Transaction processed successfully!"}, status=200)
    else:
        return JsonResponse({"error": "Fee transfer failed!"}, status=500)



logger = logging.getLogger(__name__)

# API URL for Flutterwave and other payment methods

@csrf_exempt
def process_flutterwave_payment(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        # Load the data from the request body
        data = json.loads(request.body)
        logger.info(f"Received Payment Data: {json.dumps(data, indent=2)}")

        # Validate required fields
        required_fields = ["amount", "currency", "recipient", "payment_method"]
        if not all(field in data for field in required_fields):
            return JsonResponse({"error": "Missing required fields"}, status=400)

        # Extract payment details
        amount = Decimal(str(data["amount"]))
        currency = data["currency"].upper()
        recipient_id = data["recipient"]
        payment_method = data["payment_method"].lower()
        google_pay_token = data.get("google_pay_token")
        apple_pay_token = data.get("apple_pay_token")

        # Fetch recipient details
        recipient = get_object_or_404(Recipient, id=recipient_id)
        phone_number = data.get("phone_number") or recipient.phone_number
        email = request.user.email if request.user.email else "worldttance@gmail.com"

        # Validate M-Pesa transactions (requires phone number)
        if payment_method == "m-pesa" and not phone_number:
            return JsonResponse({"error": "Phone number is required for M-Pesa payments"}, status=400)

        # Create the transaction in the database
        transaction = Transaction.objects.create(
            user=request.user,
            recipient=recipient,
            amount=amount,
            currency=currency,
            status="Pending",
            payment_method=payment_method  # Save payment method
        )
        transaction.save()

        # Prepare API payload for Flutterwave
        payload = {
            "tx_ref": f"WT_{transaction.id}",
            "amount": float(amount),
            "currency": currency,
            "payment_options": ",".join(payment_method.values()),
            "customer": {
                "email": email,
                "name": request.user.get_full_name(),
            },
            "redirect_url": settings.FLUTTERWAVE_REDIRECT_URL  # Define this URL in settings
        }

        # Add additional fields based on the payment method
        if payment_method == "m-pesa":
            payload["customer"]["phone_number"] = phone_number
            payload["phone_number"] = phone_number
        if google_pay_token:
            payload["google_pay_token"] = google_pay_token
        if apple_pay_token:
            payload["apple_pay_token"] = apple_pay_token

        logger.info(f"Sending Payment Request to Flutterwave: {json.dumps(payload, indent=2)}")

        # API Request Headers
        headers = {
            "Authorization": f"Bearer {settings.FLUTTERWAVE_SECRET_KEY}",
            "Content-Type": "application/json",
        }

        # Send request to Flutterwave API
        response = requests.post(settings.FLUTTERWAVE_API_URL, json=payload, headers=headers)
        logger.info(f"Flutterwave API Response: {response.status_code} - {response.text}")

        # Process the response from Flutterwave
        if response.status_code == 200:
            try:
                node_data = response.json()
                # Update transaction status to "Initiated"
                transaction.status = "Initiated"
                transaction.save()

                # Return the payment link from the API response
                return JsonResponse({"payment_link": node_data.get("data", {}).get("link")})
            except json.JSONDecodeError:
                return JsonResponse({"error": "Invalid JSON response from Flutterwave"}, status=500)

        return JsonResponse({"error": "Payment API error", "details": response.text}, status=500)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON payload"}, status=400)

    except Exception as e:
        logger.error(f"Payment error: {str(e)}", exc_info=True)
        return JsonResponse({"error": "Internal Server Error", "details": str(e)}, status=500)


from django.http import JsonResponse
from .models import Transaction

def transaction_status(request, transaction_id):
    try:
        transaction = Transaction.objects.get(transaction_id=transaction_id)
        return JsonResponse({"status": transaction.status})
    except Transaction.DoesNotExist:
        return JsonResponse({"error": "Transaction not found"}, status=404)
