from django.urls import path
from .views import initiate_payment,verify_payment,transfer_fees_to_admin,process_transaction_fee,process_payout
from WorldTtance.views import AdminWalletUpdateView,start_binance_transaction_check,payment_status,process_flutterwave_payment,UpdateAdminWalletView,RecipientListCreateView
from WorldTtance.views import process_payment
from WorldTtance.views import payment_status
from.utils import process_payments
from .views import payment_page,payment_failed, some_payment_selection_view,verify_payment



# Function to redirect to the default payment method
def redirect_to_default_payment(request):
    return redirect("payment_page", payment_method="default")
urlpatterns = [  

    #path('initiate-payment/', initiate_payment, name='initiate_payment'),
    path("verify/", verify_payment, name="verify_payment"),
    path("transfer_fees_to_admin/", transfer_fees_to_admin, name="transfer_fees_to_admin"),
    path("process_transaction_fee/", process_transaction_fee, name="process_transaction_fee"),



    
    #path('api/flutterwave/webhook/', flutterwave_webhook, name='flutterwave-webhook'),
    path("process_transaction_fee/", process_transaction_fee, name="process_transaction_fee"),
    path("verify_payment/", verify_payment, name="verify_payment"),




    path("process-payment/", process_payment, name="process_payment"),
    path("payment/", payment_page, name="payment_page"),
    path("payment-success/", lambda request: render(request, "success.html"), name="payment_success_page"),
    path("payment-failed/", lambda request: render(request, "failed.html"), name="payment_failed_page"),
    path('payment-failed/', payment_failed, name='payment_failed'),

    path("payment/", redirect_to_default_payment, name="payment_page"),


    path("payment-success/", lambda request: render(request, "success.html"), name="payment_success_page"),
    path("payment-failed/", payment_failed, name="payment_failed"),

    # Payment Processing
    path("payment/<str:payment_method>/", payment_page, name="payment_page"),  # Requires payment method
    path("payment/", redirect_to_default_payment, name="payment_page"),  # Redirects if no payment method is provided

    path("process-payment/", process_payments, name="process_payments"),  # Processes payments

    # Payment Method Selection
    path("choose-payment/", some_payment_selection_view, name="choose_payment_method"),

    # process payouts
    path("payout/", process_payout, name="process_payout"),

]
