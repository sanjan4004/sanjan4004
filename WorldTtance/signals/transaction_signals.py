
'''Crediting the AdminWallet with the transaction_fee
Ensuring it's only credited once per successful transaction
Updating the fee_transferred and fee_status fields'''

from django.db.models.signals import post_save
from django.dispatch import receiver
from WorldTtance.models import Transaction, AdminWallet
from decimal import Decimal

@receiver(post_save, sender=Transaction)
def transaction_fee_transfer_signal(sender, instance, created, **kwargs):
    if created and not instance.fee_transferred:
        if instance.admin_wallet and instance.transaction_fee > 0:
            instance.admin_wallet.balance += Decimal(instance.transaction_fee)
            instance.admin_wallet.save()
            instance.fee_transferred = True
            instance.fee_status = "Transferred"
            instance.save(update_fields=["fee_transferred", "fee_status"])
