from decimal import Decimal
from django.db import models
from common.models import BaseModel
from requests.models import RequestedTest

class ReferralPartner(BaseModel):
    name = models.CharField(max_length=150)
    contact_number = models.CharField(max_length=30, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))

    def __str__(self):
        return self.name

class Referral(BaseModel):
    TYPE_INCOMING = 'incoming'
    TYPE_OUTGOING = 'outgoing'
    TYPE_CHOICES = [
        (TYPE_INCOMING, 'Incoming Referral (Partner to us)'),
        (TYPE_OUTGOING, 'Outgoing Referral (Us to partner)'),
    ]

    STATUS_PENDING = 'pending'
    STATUS_SENT = 'sent'
    STATUS_RECEIVED = 'received'
    STATUS_COMPLETED = 'completed'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending Dispatch / Collection'),
        (STATUS_SENT, 'Sent / Dispatched'),
        (STATUS_RECEIVED, 'Received by Partner'),
        (STATUS_COMPLETED, 'Completed / Result Back'),
    ]

    PAYMENT_STATUS_UNPAID = 'unpaid'
    PAYMENT_STATUS_PAID = 'paid'
    PAYMENT_STATUS_NA = 'n_a'
    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_STATUS_UNPAID, 'Unpaid'),
        (PAYMENT_STATUS_PAID, 'Paid'),
        (PAYMENT_STATUS_NA, 'Not Applicable / Waived'),
    ]

    requested_test = models.ForeignKey(RequestedTest, on_delete=models.CASCADE, related_name='referrals')
    partner = models.ForeignKey(ReferralPartner, on_delete=models.CASCADE, related_name='referrals')
    referral_type = models.CharField(max_length=15, choices=TYPE_CHOICES)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=STATUS_PENDING)
    
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    commission_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    payment_status = models.CharField(max_length=15, choices=PAYMENT_STATUS_CHOICES, default=PAYMENT_STATUS_UNPAID)
    payment_date = models.DateTimeField(blank=True, null=True)
    
    notes = models.TextField(blank=True, null=True)
    referral_date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Auto-calculate commission for incoming referrals if not explicitly set
        if not self.commission_amount and self.referral_type == self.TYPE_INCOMING and self.partner.commission_rate > 0:
            self.commission_amount = self.requested_test.price_at_request * (Decimal(str(self.partner.commission_rate)) / Decimal('100.00'))
        
        # Auto-calculate amount (discount) for incoming referrals if not explicitly set
        if not self.amount and self.referral_type == self.TYPE_INCOMING and self.partner.discount_percentage > 0:
            self.amount = self.requested_test.price_at_request * (Decimal(str(self.partner.discount_percentage)) / Decimal('100.00'))
            
        super().save(*args, **kwargs)
        
        # Recalculate invoice if it is an incoming referral
        if self.referral_type == self.TYPE_INCOMING:
            test_request = self.requested_test.request
            if hasattr(test_request, 'invoice'):
                test_request.invoice.save()

    def __str__(self):
        return f"Referral of {self.requested_test.test.name} to {self.partner.name} - {self.get_status_display()}"

