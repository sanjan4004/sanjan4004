from django.db import models
from django.contrib.auth.models import User
# Create your models here.




class B2BTransaction(models.Model):
    TRANSACTION_STATUS = [
        ("PENDING", "Pending"),
        ("SUCCESS", "Success"),
        ("FAILED", "Failed"),
    ]

    transaction_id = models.CharField(max_length=100, unique=True, blank=True, null=True)
    sender_shortcode = models.CharField(max_length=10)
    receiver_shortcode = models.CharField(max_length=10)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_status = models.CharField(max_length=10, choices=TRANSACTION_STATUS, default="PENDING")
    response_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_id} - {self.transaction_status}"



