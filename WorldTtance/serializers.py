from rest_framework import serializers
from WorldTtance.models import Recipient
from WorldTtance.models import AdminWallet

class AdminWalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminWallet
        fields = '__all__'




class RecipientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipient
        fields = "__all__"  # ✅ Includes all fields in the model



from rest_framework import serializers
from .models import UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ["user", "profile_picture", "phone_number", "address", "bio"]
        read_only_fields = ["user"]


from rest_framework import serializers
from .models import Transaction

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ["id", "user", "amount",'tx_ref' ,"currency", "status", "timestamp"]



from rest_framework import serializers
from .models import KYCVerification

class KYCVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = KYCVerification
        fields = [
            "id",
            "user",
            "id_type",
            "id_number",
            "verified",
            "id_image",
            "selfie_image",
            "status",
            "submitted_at",
        ]
        read_only_fields = ["id", "user", "verified", "status", "submitted_at"]
