from django.db import models
from common.models import BaseModel

class TestCategory(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Test(BaseModel):
    STATUS_ACTIVE = 'active'
    STATUS_SUSPENDED = 'suspended'
    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Active'),
        (STATUS_SUSPENDED, 'Suspended'),
    ]

    category = models.ForeignKey(TestCategory, on_delete=models.CASCADE, related_name='tests')
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=20, unique=True)
    price = models.DecimalField(max_length=10, max_digits=10, decimal_places=2)
    turnaround_time_hours = models.PositiveIntegerField(help_text="Turnaround time in hours")
    normal_range = models.CharField(max_length=250, help_text="Reference normal range, e.g., '4.5 - 11.0' or 'Negative'")
    units = models.CharField(max_length=50, blank=True, null=True, help_text="Measurement units, e.g., 'g/dL', '10^3/uL'")
    sample_type = models.CharField(max_length=100, help_text="Type of sample needed, e.g., 'Whole Blood', 'Urine', 'Serum'")

    def __str__(self):
        return f"{self.name} ({self.code}) - {self.price}"


class TestParameter(BaseModel):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='parameters')
    name = models.CharField(max_length=150)
    normal_range = models.CharField(max_length=250, help_text="Reference normal range")
    units = models.CharField(max_length=50, blank=True, null=True, help_text="Measurement units")
    display_order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.test.name} - {self.name}"
