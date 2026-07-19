from django.db import models
from common.models import BaseModel

class Supplier(BaseModel):
    name = models.CharField(max_length=150)
    contact_name = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Reagent(BaseModel):
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=30, unique=True)
    description = models.TextField(blank=True, null=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, related_name='reagents')
    unit = models.CharField(max_length=30, help_text="e.g. Vial, Box, Kit")
    min_stock_level = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    current_quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    expiry_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.code}) - Qty: {self.current_quantity}"

class StockTransaction(BaseModel):
    TYPE_RECEIVE = 'receive'
    TYPE_ISSUE = 'issue'
    TYPE_ADJUST = 'adjust'
    TYPE_CHOICES = [
        (TYPE_RECEIVE, 'Receive Stock'),
        (TYPE_ISSUE, 'Issue Stock'),
        (TYPE_ADJUST, 'Stock Adjustment'),
    ]

    reagent = models.ForeignKey(Reagent, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=15, choices=TYPE_CHOICES)
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    reference_number = models.CharField(max_length=50, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        # Update current stock level on creation only to avoid multi-save issues
        if not self.pk:
            reagent = self.reagent
            from decimal import Decimal
            qty = Decimal(str(self.quantity))
            current = Decimal(str(reagent.current_quantity))
            if self.transaction_type == self.TYPE_RECEIVE:
                current += qty
            elif self.transaction_type == self.TYPE_ISSUE:
                current -= qty
            elif self.transaction_type == self.TYPE_ADJUST:
                current += qty
            reagent.current_quantity = current
            reagent.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.reagent.name} ({self.quantity})"
