from django.contrib import admin

# Register your models here.
from .models import B2BTransaction

class B2BTransactionAdmin(admin.ModelAdmin):
    list_display = ("transaction_id", "sender_shortcode", "receiver_shortcode", "amount", "transaction_status", "created_at")
    search_fields = ("transaction_id", "sender_shortcode", "receiver_shortcode")
    list_filter = ("transaction_status", "created_at")

admin.site.register(B2BTransaction, B2BTransactionAdmin)
