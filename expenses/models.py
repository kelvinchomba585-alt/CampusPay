from django.db import models


class Expense(models.Model):
    CATEGORY_CHOICES = [
        ("Food", "Food"),
        ("Transport", "Transport"),
        ("Education", "Education"),
        ("Entertainment", "Entertainment"),
        ("Bills", "Bills"),
        ("Other", "Other"),
    ]

    title = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default="Other"
    )
    description = models.TextField(blank=True)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Payment(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Completed", "Completed"),
        ("Failed", "Failed"),
    ]

    phone_number = models.CharField(max_length=15)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    checkout_request_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )

    merchant_request_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )

    mpesa_receipt_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Pending",
    )

    result_description = models.TextField(
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

def __str__(self):
    return f"{self.phone_number} - Ksh {self.amount} - {self.status}"