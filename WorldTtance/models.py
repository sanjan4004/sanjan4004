from django.db import models
# Create your models here.
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
import requests
import uuid
import time
import random
from django import forms
from django.core.exceptions import ValidationError
from .choices import PAYMENT_METHODS, COUNTRIES,CURRENCY_CHOICES,STATUS_CHOICES,FEE_STATUS_CHOICES,CRYPTO_CHOICES







class UserProfile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	phone_number = models.CharField(max_length=15, blank=True, null=True)
	address = models.CharField(max_length=200, blank=True, null=True)
	country = models.CharField(max_length=50, blank=True, null=True)
	date_of_birth = models.DateField(blank=True, null=True)
	profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
	kyc_verified = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)

	def profile_picture_url(self):
		if self.profile_picture and hasattr(self.profile_picture, 'url'):
			return self.profile_picture.url
		else:
			return '/static/images/default_profile_picture.jpg'  # Ensure this path is correct

	
	def __str__(self):
		return self.user.username


class Recipient(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	full_name = models.CharField(max_length=100)
	country = models.CharField(max_length=5, choices=COUNTRIES)
	currency = models.CharField(max_length=10, choices=CURRENCY_CHOICES, default=' GBP')
	mobile_wallet = models.CharField(max_length=50, blank=True, null=True)
	bank_account = models.CharField(max_length=50, blank=True, null=True)
	payment_method = models.CharField(max_length=50, choices=PAYMENT_METHODS)
	phone_number = models.CharField(max_length=15, blank=True, null=True)
	binance_pay_id = models.CharField(max_length=100, blank=True, null=True)  # Binance Pay ID

	def __str__(self):
		return f"{self.full_name} ({self.user.username})"






class KYCVerification(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	id_type = models.CharField(max_length=50, choices=[('Passport', 'Passport'), ('National ID', 'National ID'), ('Driver License', 'Driver License')])
	id_number = models.CharField(max_length=50)
	verified = models.BooleanField(default=False)
	id_image = models.ImageField(upload_to='kyc/')
	selfie_image = models.ImageField(upload_to='kyc/selfies/')
	status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')], default='Pending')
	submitted_at = models.DateTimeField(auto_now_add=True)


	def __str__(self):
		return f"KYC for {self.user.username} - {'Verified' if self.verified else 'Pending'}"






class AdminWallet(models.Model):
    admin = models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to={'is_superuser': True})
    transaction_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('3.00'))
    wallet_address = models.CharField(max_length=255, blank=True, null=True)  # Binance Wallet Address
    network = models.CharField(max_length=50, default="USDT-TRC20")  # Modify based on your needs
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))


    def deposit_fee(self, amount):
        """Deposits transaction fee into the AdminWallet"""
        self.balance += amount
        self.save()

    def __str__(self):
        if self.admin:
            return f"{self.admin.username}'s Wallet"
        return f"Admin Wallet - {self.wallet_address}"


class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipient = models.ForeignKey('Recipient', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    country = models.CharField(max_length=5, choices=COUNTRIES, default='KEN')
    currency = models.CharField(max_length=5, choices=CURRENCY_CHOICES, default='GBP')
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=4, default=Decimal('1.0'))
    transaction_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('3.00'))
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    admin_wallet = models.ForeignKey('AdminWallet', on_delete=models.SET_NULL, null=True, blank=True)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHODS)
    flutterwave_tx_id = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    transaction_reference = models.CharField(max_length=255, unique=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    fee_transferred = models.BooleanField(default=False)
    fee_status = models.CharField(max_length=20, choices=FEE_STATUS_CHOICES, default="Pending")

    # Crypto payment fields
    crypto_type = models.CharField(max_length=50, choices=CRYPTO_CHOICES, blank=True, null=True)
    crypto_address = models.CharField(max_length=255, blank=True, null=True)

    # Additional fields for different payment methods
    mpesa_phone_number = models.CharField(max_length=15, blank=True, null=True)
    card_number = models.CharField(max_length=16, blank=True, null=True)
    expiry_date = models.CharField(max_length=5, blank=True, null=True)
    cvv = models.CharField(max_length=4, blank=True, null=True)
    payment_token = models.CharField(max_length=100, blank=True, null=True)  # Google/Apple Pay
    account_number = models.CharField(max_length=20, blank=True, null=True)
    bank_name = models.CharField(max_length=100, blank=True, null=True)

    def save(self, *args, **kwargs):
        """Generate transaction reference, calculate total amount, and transfer fee to AdminWallet."""
        if not self.transaction_reference:
            timestamp = int(time.time() * 1000)  # Current time in milliseconds
            random_number = random.randint(1000, 9999)  # 4-digit random number
            self.transaction_reference = f"WT_{timestamp}{random_number}"

        # Ensure total_amount calculation uses Decimal
        self.total_amount = Decimal(self.amount) + Decimal(self.transaction_fee)

        # Only transfer fee if it hasn't been transferred before, status is 'successful', and admin_wallet exists
        if self.status == "successful" and not self.fee_transferred and self.admin_wallet:
            self.admin_wallet.balance += self.transaction_fee
            self.admin_wallet.save()
            self.fee_transferred = True
            self.fee_status = "Transferred"

        # Only run full_clean() if validation is required
        if self.payment_method == "Bank Transfer":
            self.full_clean()  # Validate before saving

        super().save(*args, **kwargs)


    def clean(self):
        """Validate required fields based on payment method."""
        if self.payment_method == "M-Pesa" and not self.mpesa_phone_number:
            raise ValidationError({"mpesa_phone_number": "Phone number is required for M-Pesa."})

        if self.payment_method in ["Visa", "MasterCard", "Amex"]:
            if not self.card_number or not self.expiry_date or not self.cvv:
                raise ValidationError({
                    "card_number": "Card number is required.",
                    "expiry_date": "Expiry date is required.",
                    "cvv": "CVV is required."
                })

        if self.payment_method in ["Google Pay", "Apple Pay"] and not self.payment_token:
            raise ValidationError({"payment_token": "Payment token is required for Google Pay and Apple Pay."})

        if self.payment_method == "Bank Transfer":
            if not self.account_number or not self.bank_name:
                raise ValidationError({
                    "account_number": "Bank account number is required.",
                    "bank_name": "Bank name is required."
                })

    def __str__(self):
        return f"Transaction {self.transaction_reference} - {self.user.username} to {self.recipient.full_name}"



class ExchangeRate(models.Model):
    base_currency = models.CharField(max_length=10)  # e.g., "USD"
    target_currency = models.CharField(max_length=10)  # e.g., "KES"
    rate = models.DecimalField(max_digits=12, decimal_places=6)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('base_currency', 'target_currency')

    def __str__(self):
        return f"{self.base_currency} to {self.target_currency}: {self.rate}"
