import logging
from django.core.management.base import BaseCommand
from patients.models import Patient

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Generate and assign unique sequential patient IDs (e.g. Lab-P000001) to all existing patients that do not have one.'

    def handle(self, *args, **options):
        # Query patients without a patient_id, ordered by primary key/created_at to assign IDs sequentially
        patients_to_update = Patient.objects.filter(patient_id__isnull=True) | Patient.objects.filter(patient_id='')
        patients_to_update = patients_to_update.order_by('created_at', 'id')

        total_patients = patients_to_update.count()
        self.stdout.write(self.style.NOTICE(f"Found {total_patients} patients without a Patient ID. Generating sequential IDs..."))

        success_count = 0
        for p in patients_to_update:
            p.save()  # Triggers save() generator override to assign sequential ID
            self.stdout.write(self.style.SUCCESS(f"Assigned ID {p.patient_id} to {p.full_name}"))
            success_count += 1

        self.stdout.write(self.style.SUCCESS(f"Successfully populated unique Patient IDs for {success_count} patients!"))
