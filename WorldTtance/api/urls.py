from django.urls import path
from .views import flutterwave_webhook, payment_webhook,verify_payment,payment_callback,update_transaction,process_payment_request,check_transaction_status,initiate_flutterwave_payment
from WorldTtance.views import process_payment
urlpatterns = [
    path("api/flutterwave/webhook/", flutterwave_webhook, name="flutterwave-webhook"),
    path("payment/webhook/", payment_webhook, name="payment-webhook"),
    path("api/flutterwave/payment_callback/", payment_callback, name="flutterwave-payment-callback"),
    path("api/update-transaction/", update_transaction, name="update-transaction"),
    path("api/flutterwave/process-payments/", process_payment_request, name="process-payments"),
    path("api/flutterwave/initiate-payment/", initiate_flutterwave_payment, name="initiate-payment"),
    path('api/flutterwave/status/', check_transaction_status, name='check_transaction_status'),
    path("api/flutterwave/verify_payment/", verify_payment, name="verify_payment"),
    path("api/flutterwave/process-payment/", process_payment, name="process_payment"),  # Proscesses payments
]
