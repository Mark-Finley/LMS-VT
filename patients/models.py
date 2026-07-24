from django.db import models
from common.models import BaseModel

class Patient(BaseModel):
    GENDER_MALE = 'M'
    GENDER_FEMALE = 'F'
    GENDER_OTHER = 'O'
    GENDER_CHOICES = [
        (GENDER_MALE, 'Male'),
        (GENDER_FEMALE, 'Female'),
        (GENDER_OTHER, 'Other'),
    ]

    patient_id = models.CharField(max_length=20, unique=True, blank=True, null=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    date_of_birth = models.DateField()
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    
    # Insurance info
    insurance_provider = models.CharField(max_length=100, blank=True, null=True)
    insurance_policy_number = models.CharField(max_length=50, blank=True, null=True)
    
    # Emergency contact
    emergency_contact_name = models.CharField(max_length=100, blank=True, null=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True, null=True)
    
    medical_history = models.TextField(blank=True, null=True)

    @property
    def full_name(self):
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"{self.full_name} ({self.date_of_birth})"

    def save(self, *args, **kwargs):
        if not self.patient_id:
            last_patient = Patient.objects.filter(patient_id__startswith='Lab-P').order_by('-patient_id').first()
            if last_patient and last_patient.patient_id:
                try:
                    last_num = int(last_patient.patient_id.split('Lab-P')[-1])
                    next_num = last_num + 1
                except ValueError:
                    next_num = Patient.objects.count() + 1
            else:
                next_num = 1
            
            while True:
                candidate = f"Lab-P{next_num:06d}"
                if not Patient.objects.filter(patient_id=candidate).exists():
                    self.patient_id = candidate
                    break
                next_num += 1
        super().save(*args, **kwargs)
