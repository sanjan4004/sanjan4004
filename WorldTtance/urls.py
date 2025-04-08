from django.urls import path,include
from .views import check_transaction_status,flutterwave_webhook,payment_callback,update_transaction,process_payment_request,initiate_flutterwave_payment
from django.contrib.auth import views as auth_views
from .views import new_transaction,complete_transaction,verify_payment,profile_view,dashboard,edit_profile,kyc_capture, process_binance_payment,new_transaction_form_view
from.import views
from django.urls import reverse
from WorldTtance.views import AdminWalletUpdateView,start_binance_transaction_check,payment_status,process_flutterwave_payment,UpdateAdminWalletView,RecipientListCreateView
from .webhook import binance_webhook
from .views import recipient_form_view
from .views import process_payment,transaction_status,payment_status,check_transaction_status,verify_payment


urlpatterns = [
    # User Profile
    path("profile/", profile_view, name="profile_view"),
    path("profile/edit/", edit_profile, name="edit_profile"),
    path("api/admin-wallet/<int:pk>/", AdminWalletUpdateView.as_view(), name="admin-wallet-update"),
    path('admin-wallet/update/', UpdateAdminWalletView.as_view(), name='update-admin-wallet'),


    # Recipient
    path('recipients/', views.recipient_list, name='recipient_list'),
    path('recipients/new/', views.new_recipient, name='new_recipient'),
    path('recipients/edit/<int:pk>/', views.recipient_edit, name='recipient_edit'),
    path('recipients/delete/<int:recipient_id>/', views.recipient_delete, name='recipient_delete'),
    path('api/recipients/', RecipientListCreateView.as_view(), name='recipient-list-create'),
    path("recipient-form/", recipient_form_view, name="recipient_form"),  #  URL for the form


    # Transactions
    path('transactions/', views.transaction_history, name='transaction_history'),
    path("transactions/new/", new_transaction, name="new_transaction"),
    path("new/", new_transaction, name="transaction_form"),  #  Ensure this exists
    path("transaction/<int:transaction_id>/complete/", complete_transaction, name="complete_transaction"),
    path("new_transaction_form/", new_transaction_form_view, name="new_transaction_form"),
    path('transaction/success/', views.transaction_success, name='transaction_success'),
    path('transaction/failed/', views.transaction_failed, name='transaction_failed'),
    

    
    # KYC Verification
    path('kyc/', views.kyc_verification, name='kyc_verification'),
    path('kyc/status/', views.kyc_status, name='kyc_status'),
    path("kyc/", kyc_capture, name="kyc_capture"),
    path("dashboard/", dashboard, name="dashboard"),
    path('accounts/', include('allauth.urls')),
    



    #password reset
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name="users/password_reset.html"), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name="users/password_reset_done.html"), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="users/password_reset_confirm.html"), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name="users/password_reset_complete.html"), name='password_reset_complete'),

    path("payment-success/", lambda request: render(request, "success.html"), name="payment-success"),
    path("payment-failed/", lambda request: render(request, "failed.html"), name="payment-failed"),
    


    #BINACE TO ADMINWALLET URLS
    path('process-binance-payment/', process_binance_payment, name='process_binance_payment'),
    path('start_binance_transaction_check/', start_binance_transaction_check, name='start_binance_transaction_check'),

    #BINANCE TRANSACTION WITHDRAW TEST
    #path("simulate-binance-withdrawal/", simulate_binance_withdrawal, name="simulate_binance_withdrawal"),





    path("api/flutterwave/webhook/", flutterwave_webhook, name="flutterwave-webhook"),
    path("payment-webhook/", flutterwave_webhook, name="flutterwave-webhook"),
    path("api/flutterwave/payment_callback/", payment_callback, name="flutterwave-payment-callback"),
    path("api/update-transaction/", update_transaction, name="update-transaction"),
    path("api/flutterwave/process-payments/", process_payment_request, name="process_payments"),# uses process_payment func
    path("api/flutterwave/initiate-payment/", initiate_flutterwave_payment, name="initiate-payment"),
    path('api/flutterwave/status/', check_transaction_status, name='check_transaction_status'),
    path("api/flutterwave/verify_payment/", verify_payment, name="verify_payment"),
    path("payment_status/", payment_status, name="payment_status"), 
    path("transaction-status/<str:transaction_id>/", transaction_status, name="transaction-status"),


    ]



#Check if images are actually saved in /media/kyc/ and /media/kyc/selfies/.
from django.conf import settings
from django.conf.urls.static import static

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
