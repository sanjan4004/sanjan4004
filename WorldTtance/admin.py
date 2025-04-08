from django.contrib import admin

# Register your models here.
from.models import Recipient,KYCVerification,Transaction,UserProfile,AdminWallet,ExchangeRate
admin.site.register(UserProfile)
admin.site.register(KYCVerification)
admin.site.register(Recipient)



@admin.register(Transaction)

class TransactionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "recipient", "amount", "currency", "payment_method", "transaction_fee", "status", "timestamp")
    search_fields = ("user__username", "recipient", "currency", "payment_method")
    list_filter = ("status", "currency", "payment_method")
    ordering = ("-timestamp",)

@admin.register(AdminWallet)
class AdminWalletAdmin(admin.ModelAdmin):
    list_display = ("admin", "wallet_address", "network","balance")





@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    list_display = ('base_currency', 'target_currency', 'rate', 'last_updated')
    list_filter = ('base_currency', 'target_currency')
    search_fields = ('base_currency', 'target_currency')
