from rest_framework import serializers

from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            "id",
            "phone_number",
            "amount",
            "checkout_request_id",
            "merchant_request_id",
            "mpesa_receipt_number",
            "status",
            "result_description",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "checkout_request_id",
            "merchant_request_id",
            "mpesa_receipt_number",
            "status",
            "result_description",
            "created_at",
        ]