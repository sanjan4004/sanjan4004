from django import forms
from .models import UserProfile, Recipient, Transaction, KYCVerification
from django.contrib.auth.models import User
from .choices import PAYMENT_METHODS, get_country_choices,CURRENCY_CHOICES,CRYPTO_CHOICES
from django.contrib.auth.forms import UserCreationForm


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["phone_number", "country", "profile_picture", "date_of_birth", "address"]


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']



class TransactionForm(forms.ModelForm):
    currency = forms.ChoiceField(choices=CURRENCY_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    country = forms.ChoiceField(choices=get_country_choices(), widget=forms.Select(attrs={'class': 'form-control'}))
    payment_method = forms.ChoiceField(choices=PAYMENT_METHODS, widget=forms.Select(attrs={'class': 'form-control'}))

    # New fields for Cryptocurrency Payments
    crypto_type = forms.ChoiceField(
        choices=CRYPTO_CHOICES, required=False, widget=forms.Select(attrs={'class': 'form-control'})
    )
    crypto_address = forms.CharField(
        required=False, max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Crypto Wallet Address'})
    )

    # Existing payment fields
    mpesa_phone_number = forms.CharField(
        required=False, max_length=15, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'M-Pesa Phone Number'})
    )
    card_number = forms.CharField(
        required=False, max_length=16, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Card Number'})
    )
    expiry_date = forms.CharField(
        required=False, max_length=5, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'MM/YY'})
    )
    cvv = forms.CharField(
        required=False, max_length=4, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'CVV'})
    )
    payment_token = forms.CharField(
        required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Google/Apple Pay Token'})
    )
    account_number = forms.CharField(
        required=False, max_length=20, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Account Number'})
    )
    bank_name = forms.CharField(
        required=False, max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Bank Name'})
    )

    class Meta:
        model = Transaction
        fields = [
            'recipient', 'amount', 'country', 'currency', 'payment_method',
            'crypto_type', 'crypto_address',  # Added Crypto Fields
            'mpesa_phone_number', 'card_number', 'expiry_date', 'cvv',
            'payment_token', 'account_number', 'bank_name'
        ]

    def clean(self):
        """Validate required fields based on payment method."""
        cleaned_data = super().clean()
        payment_method = cleaned_data.get("payment_method")

        if payment_method == "M-Pesa" and not cleaned_data.get("mpesa_phone_number"):
            self.add_error("mpesa_phone_number", "Phone number is required for M-Pesa.")

        if payment_method == "Card":
            if not cleaned_data.get("card_number") or not cleaned_data.get("expiry_date") or not cleaned_data.get("cvv"):
                self.add_error(None, "Card details (number, expiry, CVV) are required for card payments.")

        if payment_method in ["Google Pay", "Apple Pay"] and not cleaned_data.get("payment_token"):
            self.add_error("payment_token", "Payment token is required for Google Pay and Apple Pay.")

        if payment_method == "Bank Transfer":
            if not cleaned_data.get("account_number") or not cleaned_data.get("bank_name"):
                self.add_error(None, "Bank account details are required for Bank Transfers.")

        if payment_method == "Cryptocurrency":
            if not cleaned_data.get("crypto_type"):
                self.add_error("crypto_type", "Please select a cryptocurrency.")
            if not cleaned_data.get("crypto_address"):
                self.add_error("crypto_address", "Crypto wallet address is required.")

        return cleaned_data



class KYCVerificationForm(forms.ModelForm):
    class Meta:
        model = KYCVerification
        fields = ['id_type', 'id_number', 'id_image', 'selfie_image','verified']
        widgets = {
            'id_type': forms.Select(attrs={'class': 'form-control'}),
            'id_number': forms.TextInput(attrs={'class': 'form-control'}),
            'id_image': forms.FileInput(attrs={'class': 'form-control'}),
            'selfie_image': forms.FileInput(attrs={'class': 'form-control'}),
        }


class RecipientEditForm(forms.ModelForm):
    class Meta:
        model = Recipient
        fields = ['full_name', 'country', 'currency', 'mobile_wallet', 'bank_account', 'payment_method','phone_number','binance_pay_id']
    
    
    def clean(self):
        cleaned_data = super().clean()
        payment_method = cleaned_data.get('payment_method')
        phone_number = cleaned_data.get('phone_number')

        if payment_method == "M-Pesa" and not phone_number:
            self.add_error('phone_number', "Phone number is required for M-Pesa payments.")


        return cleaned_data


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

        

class RecipientForm(forms.ModelForm):
    currency = forms.ChoiceField(
        choices=CURRENCY_CHOICES, 
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    country = forms.ChoiceField(
        choices=get_country_choices(), 
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    payment_method = forms.ChoiceField(
        choices=PAYMENT_METHODS, 
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    # Additional fields for specific payment methods
    card_number = forms.CharField(
        required=False, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Card Number'})
    )
    expiry_date = forms.CharField(
        required=False, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'MM/YY'})
    )
    cvv = forms.CharField(
        required=False, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'CVV'})
    )
    token = forms.CharField(
        required=False, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Google Pay/Apple Pay Token'})
    )
    bank_account_number = forms.CharField(
        required=False, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Bank Account Number'})
    )

    class Meta:
        model = Recipient
        fields = [
            'full_name', 'country', 'currency', 'mobile_wallet', 
            'bank_account', 'binance_pay_id', 'payment_method', 
            'phone_number', 'card_number', 'expiry_date', 'cvv', 
            'token', 'bank_account_number'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'currency': forms.TextInput(attrs={'class': 'form-control'}),
            'mobile_wallet': forms.TextInput(attrs={'class': 'form-control'}),
            'bank_account': forms.TextInput(attrs={'class': 'form-control'}),
            'binance_pay_id': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number (for M-Pesa)'}),
        }

    def clean(self):
        """
        Ensure that required fields are provided based on the selected payment method.
        """
        cleaned_data = super().clean()
        payment_method = cleaned_data.get('payment_method')

        if payment_method == "M-Pesa" and not cleaned_data.get('phone_number'):
            self.add_error('phone_number', "Phone number is required for M-Pesa payments.")

        elif payment_method in ["Visa", "MasterCard", "Amex"]:
            if not cleaned_data.get('card_number'):
                self.add_error('card_number', "Card number is required for card payments.")
            if not cleaned_data.get('expiry_date'):
                self.add_error('expiry_date', "Expiry date is required for card payments.")
            if not cleaned_data.get('cvv'):
                self.add_error('cvv', "CVV is required for card payments.")

        elif payment_method in ["Google Pay", "Apple Pay"] and not cleaned_data.get('token'):
            self.add_error('token', "Token is required for Google Pay and Apple Pay.")

        elif payment_method == "Bank Transfer" and not cleaned_data.get('bank_account_number'):
            self.add_error('bank_account_number', "Bank account number is required for bank transfers.")

        return cleaned_data
