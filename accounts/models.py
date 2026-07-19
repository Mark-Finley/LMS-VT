from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_ADMINISTRATOR = 'administrator'
    ROLE_LAB_MANAGER = 'laboratory_manager'
    ROLE_PATHOLOGIST = 'pathologist'
    ROLE_LAB_SCIENTIST = 'laboratory_scientist'
    ROLE_LAB_TECHNICIAN = 'laboratory_technician'
    ROLE_RECEPTIONIST = 'receptionist'
    ROLE_CASHIER = 'cashier'
    ROLE_STORE_OFFICER = 'store_officer'
    ROLE_QUALITY_OFFICER = 'quality_officer'
    ROLE_DOCTOR = 'doctor'
    ROLE_PATIENT = 'patient'
    
    ROLE_CHOICES = [
        (ROLE_ADMINISTRATOR, 'Administrator'),
        (ROLE_LAB_MANAGER, 'Laboratory Manager'),
        (ROLE_PATHOLOGIST, 'Pathologist'),
        (ROLE_LAB_SCIENTIST, 'Laboratory Scientist'),
        (ROLE_LAB_TECHNICIAN, 'Laboratory Technician'),
        (ROLE_RECEPTIONIST, 'Receptionist'),
        (ROLE_CASHIER, 'Cashier'),
        (ROLE_STORE_OFFICER, 'Store Officer'),
        (ROLE_QUALITY_OFFICER, 'Quality Officer'),
        (ROLE_DOCTOR, 'Doctor'),
        (ROLE_PATIENT, 'Patient'),
    ]

    role = models.CharField(
        max_length=30,
        choices=ROLE_CHOICES,
        default=ROLE_RECEPTIONIST,
    )
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    signature = models.ImageField(upload_to='signatures/', blank=True, null=True)
    patient = models.ForeignKey(
        'patients.Patient',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='user_accounts'
    )

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
