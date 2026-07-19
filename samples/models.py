from django.db import models
from django.conf import settings
from common.models import BaseModel
from requests.models import TestRequest

class Sample(BaseModel):
    STATUS_COLLECTED = 'collected'
    STATUS_RECEIVED = 'received'
    STATUS_PROCESSING = 'processing'
    STATUS_TESTING = 'testing'
    STATUS_COMPLETED = 'completed'
    STATUS_ARCHIVED = 'archived'
    STATUS_REJECTED = 'rejected'

    STATUS_CHOICES = [
        (STATUS_COLLECTED, 'Collected'),
        (STATUS_RECEIVED, 'Received in Lab'),
        (STATUS_PROCESSING, 'Processing'),
        (STATUS_TESTING, 'Testing'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_ARCHIVED, 'Archived'),
        (STATUS_REJECTED, 'Rejected'),
    ]

    request = models.ForeignKey(TestRequest, on_delete=models.CASCADE, related_name='samples')
    sample_type = models.CharField(max_length=100)
    barcode_number = models.CharField(max_length=50, unique=True, db_index=True)
    
    collected_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='collected_samples'
    )
    collected_at = models.DateTimeField(null=True, blank=True)
    
    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='received_samples'
    )
    received_at = models.DateTimeField(null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_COLLECTED)
    rejection_reason = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.barcode_number:
            import datetime
            import random
            date_str = datetime.datetime.now().strftime("%Y%m%d")
            rand_str = ''.join(random.choices("0123456789", k=6))
            self.barcode_number = f"SMP-{date_str}-{rand_str}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.barcode_number} - {self.sample_type} ({self.get_status_display()})"

class SampleTrackingLog(BaseModel):
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE, related_name='tracking_logs')
    scanned_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    status_to = models.CharField(max_length=30)
    notes = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sample.barcode_number} -> {self.status_to} at {self.timestamp}"
