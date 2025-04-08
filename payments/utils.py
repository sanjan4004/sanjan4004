import requests
import logging
import json
import time
import hmac
import hashlib
from decimal import Decimal
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.conf import settings
from WorldTtance.models import Transaction, Recipient

logger = logging.getLogger(__name__)

PAYMENT_APIS = {
    "flutterwave": "FLUTTERWAVE_NODE_API",  # Replace with actual URL

}

@csrf_exempt
def process_payments(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        data = json.loads(request.body)
        logger.info(f"Received Data: {json.dumps(data, indent=2)}")
        
        required_fields = ["amount", "currency", "recipient", "payment_method"]
        if not all(field in data for field in required_fields):
            return JsonResponse({"error": "Missing required fields"}, status=400)
        
        amount = Decimal(str(data["amount"]))
        currency = data["currency"].upper()
        recipient_id = data["recipient"]
        payment_method = data["payment_method"].lower()
        google_pay_token = data.get("google_pay_token")
        apple_pay_token = data.get("apple_pay_token")

        recipient = get_object_or_404(Recipient, id=recipient_id)
        phone_number = data.get("phone_number") or recipient.phone_number
        email = request.user.email if request.user.email else "worldttance@gmail.com"

        if payment_method == "m-pesa" and not phone_number:
            return JsonResponse({"error": "Phone number is required for M-Pesa payments"}, status=400)
        
        transaction = Transaction.objects.create(
            user=request.user,
            recipient=recipient,
            amount=amount,
            currency=currency,
            status="Pending"
        )
        
        payload = {
            "tx_ref": f"WT_{transaction.id}",
            "amount": float(amount),
            "currency": currency,
            "payment_options": payment_method,
            "customer": {
                "email": email,
                "name": request.user.get_full_name(),
            },
            "redirect_url": "http://127.0.0.1:8000/payment/flutterwave/callback/"
        }

        if payment_method == "m-pesa":
            payload["customer"]["phone_number"] = phone_number
            payload["phone_number"] = phone_number
        
        if google_pay_token:
            payload["google_pay_token"] = google_pay_token
        if apple_pay_token:
            payload["apple_pay_token"] = apple_pay_token

        logger.info(f"Sending to API: {json.dumps(payload, indent=2)}")
        url = PAYMENT_APIS.get(payment_method)
        if not url:
            return JsonResponse({"error": "Invalid payment method"}, status=400)

        headers = {
            "Authorization": f"Bearer {settings.BINANCE_SECRET_KEY}",
            "Content-Type": "application/json",
        }

        response = requests.post(url, json=payload, headers=headers)
        logger.info(f"API Response: {response.status_code} - {response.text}")

        if response.status_code == 200:
            try:
                node_data = response.json()
                transaction.status = "Initiated"
                transaction.save()
                return JsonResponse({"payment_link": node_data.get("payment_link")})
            except json.JSONDecodeError:
                return JsonResponse({"error": "Invalid JSON response from API"}, status=500)

        return JsonResponse({"error": "Payment API error", "details": response.text}, status=500)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON payload"}, status=400)

    except Exception as e:
        logger.error(f"Payment error: {str(e)}", exc_info=True)
        return JsonResponse({"error": "Internal Server Error", "details": str(e)}, status=500)
