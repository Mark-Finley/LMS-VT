from django.db import models
from django.conf import settings
from common.models import BaseModel
from requests.models import RequestedTest
from samples.models import Sample
from test_catalogue.models import TestParameter

class Result(BaseModel):
    STATUS_DRAFT = 'draft'
    STATUS_REVIEWED = 'reviewed'
    STATUS_VERIFIED = 'verified'
    STATUS_RELEASED = 'released'

    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Draft'),
        (STATUS_REVIEWED, 'Reviewed / Pending Verification'),
        (STATUS_VERIFIED, 'Verified by Pathologist'),
        (STATUS_RELEASED, 'Released to Patient'),
    ]

    requested_test = models.OneToOneField(RequestedTest, on_delete=models.CASCADE, related_name='result')
    sample = models.ForeignKey(Sample, on_delete=models.SET_NULL, null=True, blank=True, related_name='results')
    
    # Store value as string for flexibility (numeric/text results)
    value = models.CharField(max_length=255, help_text="Result value, e.g., '14.2' or 'Positive'")
    value_numeric = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True, help_text="Optional parsed numeric value for graphing/ranges")
    
    is_critical = models.BooleanField(default=False)
    interpretation = models.TextField(blank=True, null=True, help_text="Auto or technician interpretation notes")
    
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='recorded_results'
    )
    recorded_at = models.DateTimeField(null=True, blank=True)
    
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_results'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_results'
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    
    # Electronic signature capture (pathologist signature image or text description)
    electronic_signature = models.TextField(blank=True, null=True, help_text="Digitally signed hash/stamp or reference to Pathologist's signature image")

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)

    def __str__(self):
        return f"Result for {self.requested_test.test.name} - Val: {self.value} [{self.get_status_display()}]"


class ParameterResultValue(BaseModel):
    FLAG_NORMAL = 'N'
    FLAG_HIGH = 'H'
    FLAG_LOW = 'L'
    FLAG_CHOICES = [
        (FLAG_NORMAL, 'Normal'),
        (FLAG_HIGH, 'High'),
        (FLAG_LOW, 'Low'),
    ]

    result = models.ForeignKey(Result, on_delete=models.CASCADE, related_name='parameter_values')
    parameter = models.ForeignKey(TestParameter, on_delete=models.CASCADE)
    value = models.CharField(max_length=255, help_text="Sub-parameter result value, e.g. '14.2' or 'Normal'")
    flag = models.CharField(max_length=5, choices=FLAG_CHOICES, default=FLAG_NORMAL)

    def __str__(self):
        return f"{self.parameter.name}: {self.value} ({self.flag})"
