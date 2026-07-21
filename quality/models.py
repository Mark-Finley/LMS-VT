from django.db import models
from common.models import BaseModel

class QCControl(BaseModel):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=100, default='General')
    lot_number = models.CharField(max_length=50, unique=True)
    expiry_date = models.DateField()
    target_value = models.CharField(max_length=50, help_text="e.g. 5.0, Normal, Negative")
    standard_deviation = models.DecimalField(max_digits=8, decimal_places=4, default=0.0000, help_text="Acceptable standard deviation")

    def __str__(self):
        return f"{self.name} (Lot: {self.lot_number})"

class QCRun(BaseModel):
    STATUS_PASS = 'pass'
    STATUS_FAIL = 'fail'
    STATUS_CHOICES = [
        (STATUS_PASS, 'Pass'),
        (STATUS_FAIL, 'Fail'),
    ]

    control = models.ForeignKey(QCControl, on_delete=models.CASCADE, related_name='runs')
    run_date = models.DateTimeField(auto_now_add=True)
    value = models.CharField(max_length=50)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"QC Run #{self.id} for {self.control.name} - {self.get_status_display()}"

class NonConformance(BaseModel):
    STATUS_OPEN = 'open'
    STATUS_CLOSED = 'closed'
    STATUS_CHOICES = [
        (STATUS_OPEN, 'Open (Pending Review)'),
        (STATUS_CLOSED, 'Closed (Resolved)'),
    ]

    title = models.CharField(max_length=150)
    description = models.TextField()
    date_identified = models.DateField()
    corrective_action = models.TextField(blank=True, null=True, help_text="CAPA (Corrective and Preventive Action) notes")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=STATUS_OPEN)

    def __str__(self):
        return f"NC: {self.title} [{self.get_status_display()}]"
