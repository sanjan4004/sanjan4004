import hmac
import hashlib
import json
import time
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from django.conf import settings
BINANCE_SECRET_KEY = getattr(settings, "BINANCE_ADMIN_WALLET", {}).get("api_secret")


@csrf_exempt
def binance_webhook(request):
    if request.method == "POST":
        try:
            payload = json.loads(request.body)

            # Verify the Binance signature
            received_signature = request.headers.get("X-MBX-SIGNATURE")
            timestamp = request.headers.get("X-MBX-TIMESTAMP")

            if not received_signature or not timestamp:
                return JsonResponse({"error": "Invalid request headers"}, status=400)

            # Recreate the signature
            query_string = json.dumps(payload, separators=(',', ':'))
            expected_signature = hmac.new(
                BINANCE_SECRET_KEY.encode(),
                query_string.encode(),
                hashlib.sha256
            ).hexdigest()

            if received_signature != expected_signature:
                return JsonResponse({"error": "Invalid signature"}, status=403)

            # Process the webhook data
            transaction_id = payload.get("transactionId")
            status = payload.get("status")

            if status == "COMPLETED":
                # Update transaction in the database
                print(f"Transaction {transaction_id} completed successfully!")

            elif status == "FAILED":
                print(f"Transaction {transaction_id} failed.")

            return JsonResponse({"message": "Webhook processed successfully"})

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)
