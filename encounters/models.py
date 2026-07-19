from django.db import models
from django.conf import settings
from common.models import BaseModel
from patients.models import Patient

class Encounter(BaseModel):
    TYPE_OUTPATIENT = 'outpatient'
    TYPE_INPATIENT = 'inpatient'
    TYPE_EMERGENCY = 'emergency'
    TYPE_WALKIN = 'walk_in'
    
    TYPE_CHOICES = [
        (TYPE_OUTPATIENT, 'Outpatient'),
        (TYPE_INPATIENT, 'Inpatient'),
        (TYPE_EMERGENCY, 'Emergency'),
        (TYPE_WALKIN, 'Walk-in'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='encounters')
    encounter_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_WALKIN)
    
    # Internal doctor assignment
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': 'doctor'},
        related_name='doctor_encounters'
    )
    
    # External referring doctor
    referring_physician = models.CharField(max_length=100, blank=True, null=True)
    
    clinical_notes = models.TextField(blank=True, null=True)
    diagnosis = models.TextField(blank=True, null=True)
    encounter_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Encounter {self.id} - {self.patient.full_name} ({self.get_encounter_type_display()})"
