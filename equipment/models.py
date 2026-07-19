from django.db import models
from common.models import BaseModel

class Equipment(BaseModel):
    STATUS_ACTIVE = 'active'
    STATUS_OFFLINE = 'offline'
    STATUS_MAINTENANCE = 'maintenance'
    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Active'),
        (STATUS_OFFLINE, 'Offline'),
        (STATUS_MAINTENANCE, 'Under Maintenance'),
    ]

    name = models.CharField(max_length=150)
    model = models.CharField(max_length=100)
    serial_number = models.CharField(max_length=100, unique=True)
    manufacturer = models.CharField(max_length=100)
    purchase_date = models.DateField(null=True, blank=True)
    last_calibration_date = models.DateField(null=True, blank=True)
    next_calibration_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)

    def __str__(self):
        return f"{self.name} ({self.serial_number}) - {self.get_status_display()}"

class MaintenanceLog(BaseModel):
    TYPE_CALIBRATION = 'calibration'
    TYPE_PREVENTIVE = 'preventive'
    TYPE_REPAIR = 'repair'
    TYPE_CHOICES = [
        (TYPE_CALIBRATION, 'Calibration Run'),
        (TYPE_PREVENTIVE, 'Preventive Maintenance'),
        (TYPE_REPAIR, 'Repair Downtime'),
    ]

    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='maintenance_logs')
    maintenance_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    performed_by_name = models.CharField(max_length=150, help_text="Name of engineer or technician")
    notes = models.TextField(blank=True, null=True)
    cost = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.maintenance_type == self.TYPE_CALIBRATION and self.end_date:
            eq = self.equipment
            eq.last_calibration_date = self.end_date.date()
            import datetime
            eq.next_calibration_date = eq.last_calibration_date + datetime.timedelta(days=182) # approx 6 months
            eq.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_maintenance_type_display()} on {self.equipment.name} by {self.performed_by_name}"
