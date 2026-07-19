from decimal import Decimal
from django.db import models
from django.conf import settings
from common.models import BaseModel
from patients.models import Patient
from requests.models import TestRequest

class Invoice(BaseModel):
    STATUS_UNPAID = 'unpaid'
    STATUS_PARTIAL = 'partial'
    STATUS_PAID = 'paid'
    STATUS_CHOICES = [
        (STATUS_UNPAID, 'Unpaid'),
        (STATUS_PARTIAL, 'Partial Payment'),
        (STATUS_PAID, 'Fully Paid'),
    ]

    request = models.OneToOneField(TestRequest, on_delete=models.CASCADE, related_name='invoice')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='invoices')
    
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    payable_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    balance_due = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    
    payment_status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=STATUS_UNPAID)

    def calculate_totals(self):
        # Sum requested tests
        requested_tests = self.request.requested_tests.all()
        # Sum returning a decimal if tests exist, else 0. Convert to Decimal.
        total = Decimal(str(sum(rt.price_at_request for rt in requested_tests) or '0.00'))
        self.total_amount = total
        
        # Cast to Decimal in case float defaults persist during creation
        discount = Decimal(str(self.discount_amount or '0.00'))
        tax = Decimal(str(self.tax_amount or '0.00'))
        paid = Decimal(str(self.paid_amount or '0.00'))
        
        self.payable_amount = total - discount + tax
        self.balance_due = self.payable_amount - paid
        
        if paid <= 0:
            self.payment_status = self.STATUS_UNPAID
        elif self.balance_due <= 0:
            self.payment_status = self.STATUS_PAID
            self.balance_due = Decimal('0.00')
        else:
            self.payment_status = self.STATUS_PARTIAL

    def save(self, *args, **kwargs):
        self.calculate_totals()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Invoice {self.id} for {self.patient.full_name} - Due: {self.balance_due}"

class Payment(BaseModel):
    METHOD_CASH = 'cash'
    METHOD_CARD = 'card'
    METHOD_MOBILE_MONEY = 'mobile_money'
    METHOD_INSURANCE = 'insurance'
    METHOD_BANK_TRANSFER = 'bank_transfer'

    METHOD_CHOICES = [
        (METHOD_CASH, 'Cash'),
        (METHOD_CARD, 'Credit/Debit Card'),
        (METHOD_MOBILE_MONEY, 'Mobile Money'),
        (METHOD_INSURANCE, 'Insurance'),
        (METHOD_BANK_TRANSFER, 'Bank Transfer'),
    ]

    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments')
    payment_method = models.CharField(max_length=20, choices=METHOD_CHOICES, default=METHOD_CASH)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_reference = models.CharField(max_length=100, blank=True, null=True)
    payment_date = models.DateTimeField(auto_now_add=True)
    
    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='received_payments'
    )

    def save(self, *args, **kwargs):
        # Run standard save
        super().save(*args, **kwargs)
        # Update invoice payment totals
        invoice = self.invoice
        payments_sum = sum(p.amount_paid for p in invoice.payments.all())
        invoice.paid_amount = payments_sum
        invoice.save()

        # Update the associated request payment status
        request = invoice.request
        if invoice.payment_status == Invoice.STATUS_PAID:
            request.payment_status = TestRequest.PAYMENT_PAID
        elif invoice.payment_status == Invoice.STATUS_PARTIAL:
            request.payment_status = TestRequest.PAYMENT_PARTIAL
        else:
            request.payment_status = TestRequest.PAYMENT_UNPAID
        request.save()

    def __str__(self):
        return f"Payment {self.id} for Invoice {self.invoice.id} - Amount: {self.amount_paid}"

class Receipt(BaseModel):
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='receipt')
    receipt_number = models.CharField(max_length=50, unique=True, db_index=True)
    issued_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.receipt_number:
            import datetime
            import random
            date_str = datetime.datetime.now().strftime("%Y%m%d")
            rand_str = ''.join(random.choices("0123456789", k=5))
            self.receipt_number = f"REC-{date_str}-{rand_str}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Receipt {self.receipt_number} for Payment {self.payment.id}"
