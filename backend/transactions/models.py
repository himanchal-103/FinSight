from django.db import models

# Create your models here.
class Transaction(models.Model):
    class TransactionType(models.TextChoices):
        DEPOSIT = "deposit", "Deposit"
        WITHDRAWN = "withdrawn", "Withdrawn"

    class TransactionCategory(models.TextChoices):
        PAYROLL = "payroll", "Payroll"
        PARTS_PURCHASE = "parts_purchase", "Parts Purchase"
        SHOP_EXPENSE = "shop_expense", "Shop Expense"
        SERVICE_CHARGE = "service_charge", "Service Charge"

    id = models.AutoField(primary_key=True)
    transaction_at = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    transaction_type = models.CharField(max_length=10, choices=TransactionType.choices)
    category = models.CharField(max_length=20, choices=TransactionCategory.choices)
    description = models.CharField(max_length=255)

    class Meta:
        ordering = ["-transaction_at"]

    def __str__(self):
        return f"{self.transaction_type} - {self.category}"