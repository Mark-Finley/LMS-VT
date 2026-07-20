from django.db import models
from django.conf import settings
from common.models import BaseModel
from encounters.models import Encounter
from test_catalogue.models import Test

class TestRequest(BaseModel):
    PRIORITY_ROUTINE = 'routine'
    PRIORITY_URGENT = 'urgent'
    PRIORITY_STAT = 'stat'
    
    PRIORITY_CHOICES = [
        (PRIORITY_ROUTINE, 'Routine'),
        (PRIORITY_URGENT, 'Urgent'),
        (PRIORITY_STAT, 'STAT'),
    ]

    PAYMENT_UNPAID = 'unpaid'
    PAYMENT_PAID = 'paid'
    PAYMENT_PARTIAL = 'partial'
    PAYMENT_WAIVED = 'waived'

    PAYMENT_CHOICES = [
        (PAYMENT_UNPAID, 'Unpaid'),
        (PAYMENT_PAID, 'Paid'),
        (PAYMENT_PARTIAL, 'Partial'),
        (PAYMENT_WAIVED, 'Waived'),
    ]

    encounter = models.ForeignKey(Encounter, on_delete=models.CASCADE, related_name='requests')
    request_number = models.CharField(max_length=50, unique=True, db_index=True)
    priority = models.CharField(max_length=15, choices=PRIORITY_CHOICES, default=PRIORITY_ROUTINE)
    payment_status = models.CharField(max_length=15, choices=PAYMENT_CHOICES, default=PAYMENT_UNPAID)
    request_date = models.DateTimeField(auto_now_add=True)
    
    ordered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ordered_requests'
    )
    
    tests = models.ManyToManyField(Test, through='RequestedTest', related_name='requests')

    def save(self, *args, **kwargs):
        if not self.request_number:
            # Generate a unique request number if not provided
            import datetime
            import random
            date_str = datetime.datetime.now().strftime("%Y%m%d")
            while True:
                rand_str = ''.join(random.choices("0123456789", k=6))
                candidate = f"REQ-{date_str}-{rand_str}"
                if not TestRequest.objects.filter(request_number=candidate).exists():
                    self.request_number = candidate
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.request_number} ({self.priority.upper()})"

class RequestedTest(BaseModel):
    STATUS_PENDING = 'pending'
    STATUS_COLLECTED = 'collected'
    STATUS_RECEIVED = 'received'
    STATUS_TESTING = 'testing'
    STATUS_COMPLETED = 'completed'
    STATUS_VERIFIED = 'verified'
    STATUS_RELEASED = 'released'
    STATUS_REJECTED = 'rejected'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending Payment/Collection'),
        (STATUS_COLLECTED, 'Sample Collected'),
        (STATUS_RECEIVED, 'Sample Received in Lab'),
        (STATUS_TESTING, 'Testing in Progress'),
        (STATUS_COMPLETED, 'Completed / Result Entered'),
        (STATUS_VERIFIED, 'Supervisor Verified'),
        (STATUS_RELEASED, 'Result Released'),
        (STATUS_REJECTED, 'Sample Rejected'),
    ]

    request = models.ForeignKey(TestRequest, on_delete=models.CASCADE, related_name='requested_tests')
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='requested_tests')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    price_at_request = models.DecimalField(max_length=10, max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        if not self.price_at_request and self.test:
            self.price_at_request = self.test.price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.request.request_number} - {self.test.name} [{self.get_status_display()}]"
