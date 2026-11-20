from django.contrib import admin
from .models import Expense, Payment


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("title", "amount", "category", "date", "created_at")
    list_filter = ("category", "date")
    search_fields = ("title", "description")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "phone_number",
        "amount",
        "status",
        "mpesa_receipt_number",
        "created_at",
    )

    list_filter = ("status", "created_at")
    search_fields = (
        "phone_number",
        "mpesa_receipt_number",
        "checkout_request_id",
    )