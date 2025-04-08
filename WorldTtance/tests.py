from django.test import TestCase
from django.contrib.auth.models import User
from WorldTtance.models import AdminWallet, UserProfile, Recipient, Transaction, KYCVerification
from decimal import Decimal
from rest_framework.test import APITestCase  # Import APITestCase
from django.test import TestCase
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from django.urls import reverse
from WorldTtance.models import AdminWallet, UserProfile, Recipient, Transaction, KYCVerification
from rest_framework import status
from decimal import Decimal

from rest_framework.test import APITestCase
from django.urls import reverse

from rest_framework.test import APIClient  # ✅ Import APIClient
from WorldTtance.models import Recipient



class BaseTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.admin = User.objects.create_superuser(username="admin", password="adminpassword")

        self.admin_wallet = AdminWallet.objects.create(admin=self.admin, balance=Decimal("1000.00"))

        # Avoid duplicate UserProfile creation
        self.user_profile, created = UserProfile.objects.get_or_create(user=self.user, phone_number="123456789")

        self.client.login(username="testuser", password="testpassword")



class RecipientTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.recipient = Recipient.objects.create(
            user=self.user, full_name="John Doe", country="Kenya", currency="KES", payment_method="Mobile Money"
        )
    
    def test_recipient_creation(self):
        self.assertEqual(self.recipient.full_name, "John Doe")
        self.assertEqual(self.recipient.currency, "KES")

class KYCVerificationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.kyc = KYCVerification.objects.create(
            user=self.user, id_type="Passport", id_number="12345678", verified=False, status="Pending"
        )
    
    def test_kyc_creation(self):
        self.assertEqual(self.kyc.user.username, "testuser")
        self.assertEqual(self.kyc.status, "Pending")



def tearDown(self):
    UserProfile.objects.all().delete()





class AdminWalletAPITestCase(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(username="admin", password="password")
        self.client.force_authenticate(user=self.admin)  # Authenticate as admin

        self.admin_wallet = AdminWallet.objects.create(admin=self.admin, balance=100.00)

    def test_update_admin_wallet_balance(self):
        url = f"/api/admin-wallet/{self.admin_wallet.id}/"
        data = {"balance": 200.00}

        response = self.client.patch(url, data, format="json")
        self.admin_wallet.refresh_from_db()

        self.assertEqual(response.status_code, 200)  # ✅ Ensure success response
        self.assertEqual(float(self.admin_wallet.balance), 200.00)  # ✅ Ensure balance is updated




class RecipientAPITestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.recipient = Recipient.objects.create(
            user=self.user,
            full_name="John Doe",
            country="Kenya",
            currency="KES",
            payment_method="M-Pesa",
        )

    def test_new_recipient(self):
        """Ensure a recipient can be created."""
        url = reverse("recipient-create")
        data = {"user": self.user.id, "full_name": "Jane Doe", "country": "Kenya", "currency": "KES", "payment_method": "Bank"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list_recipients(self):
        """Ensure recipients can be listed."""
        url = reverse("recipient-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class RecipientAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.login(username="testuser", password="testpassword")

    def test_new_recipient(self):
        data = {
            "full_name": "John Doe",
            "country": "Kenya",
            "mobile_wallet": "M-Pesa",
        }
        response = self.client.post("/api/recipients/", data)  # ❌ Possible wrong URL
        self.assertEqual(response.status_code, 201)  # ✅ Expecting success




class BaseTestCase(APITestCase):  # Now APITestCase is properly imported
    def setUp(self):
        """Set up test data for API testing."""
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.admin = User.objects.create_superuser(username="admin", password="adminpassword")

        self.admin_wallet = AdminWallet.objects.create(admin=self.admin, balance=Decimal("1000.00"))

        # Ensure UserProfile is only created if it does not exist
        self.user_profile, created = UserProfile.objects.get_or_create(user=self.user, phone_number="123456789")

        self.client.login(username="testuser", password="testpassword")
