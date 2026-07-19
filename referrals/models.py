from django.db import models
from common.models import BaseModel
from requests.models import RequestedTest

class ReferralPartner(BaseModel):
    name = models.CharField(max_length=150)
    contact_number = models.CharField(max_length=30, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)

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

    requested_test = models.ForeignKey(RequestedTest, on_delete=models.CASCADE, related_name='referrals')
    partner = models.ForeignKey(ReferralPartner, on_delete=models.CASCADE, related_name='referrals')
    referral_type = models.CharField(max_length=15, choices=TYPE_CHOICES)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=STATUS_PENDING)
    notes = models.TextField(blank=True, null=True)
    referral_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Referral of {self.requested_test.test.name} to {self.partner.name} - {self.get_status_display()}"
