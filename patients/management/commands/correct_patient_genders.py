import logging
from django.core.management.base import BaseCommand
from patients.models import Patient

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Check all existing patients first names and correct their gender choices to Male (M) or Female (F).'

    # Known name mappings
    MALE_NAMES = {
        'benjamin', 'caleb', 'daniel', 'dennis', 'ebenezer', 'edward', 'emmanuel',
        'francis', 'gideon', 'isaac', 'joshua', 'kofi', 'kojo', 'kwame', 'richmond',
        'samuel', 'solomon', 'yaw', 'john', 'david', 'james', 'robert', 'michael',
        'william', 'joseph', 'charles', 'thomas', 'christopher', 'matthew', 'anthony',
        'mark', 'donald', 'steven', 'paul', 'andrew', 'kenneth', 'kevin', 'brian',
        'george', 'timothy', 'ronald', 'jeffrey', 'ryan', 'jacob', 'gary', 'nicholas',
        'eric', 'jonathan', 'stephen', 'larry', 'justin', 'scott', 'brandon', 'gregory',
        'alexander', 'frank', 'patrick', 'raymond', 'jack', 'jerry', 'tyler', 'aaron',
        'jose', 'adam', 'nathan', 'henry', 'douglas', 'zachary', 'peter', 'kyle',
        'walter', 'harold', 'jeremy', 'ethan', 'carl', 'albert', 'arthur', 'gerald',
        'lawrence', 'roger', 'kwabena', 'kwasi', 'kwadwo'
    }

    FEMALE_NAMES = {
        'abena', 'akua', 'alice', 'ama', 'bernice', 'dorothy', 'efia', 'eunice',
        'grace', 'harriet', 'josephine', 'mavis', 'patricia', 'phyllis', 'priscilla',
        'rachel', 'mary', 'jennifer', 'linda', 'elizabeth', 'barbara', 'susan',
        'jessica', 'sarah', 'karen', 'nancy', 'lisa', 'betty', 'margaret', 'sandra',
        'ashley', 'kimberly', 'emily', 'donna', 'michelle', 'carol', 'amanda',
        'melissa', 'deborah', 'stephanie', 'rebecca', 'sharon', 'laura', 'cynthia',
        'kathleen', 'amy', 'shirley', 'angela', 'helen', 'anna', 'brenda', 'pamela',
        'nicole', 'samantha', 'katherine', 'christine', 'debora', 'carolyn', 'janet',
        'catherine', 'maria', 'heather', 'diane', 'virginia', 'julie', 'joyce',
        'evelyn', 'joan', 'victoria', 'kelly', 'christina', 'lauren', 'frances',
        'martha', 'judith', 'cheryl', 'megan', 'andrea', 'ann', 'jean', 'doris',
        'jacqueline', 'yaaa', 'afua', 'afia', 'yeboah', 'esi', 'adwoa', 'aba'
    }

    def handle(self, *args, **options):
        patients = Patient.objects.all()
        total_audited = 0
        total_corrected = 0
        unrecognized = []

        self.stdout.write(self.style.NOTICE(f"Auditing gender values for {patients.count()} patient records..."))

        for p in patients:
            total_audited += 1
            first_name_lower = p.first_name.strip().lower()

            inferred_gender = None
            if first_name_lower in self.MALE_NAMES:
                inferred_gender = Patient.GENDER_MALE
            elif first_name_lower in self.FEMALE_NAMES:
                inferred_gender = Patient.GENDER_FEMALE

            if inferred_gender:
                if p.gender != inferred_gender:
                    old_gender = p.get_gender_display()
                    p.gender = inferred_gender
                    p.save()
                    new_gender = p.get_gender_display()
                    self.stdout.write(self.style.SUCCESS(
                        f"Corrected {p.full_name}: '{old_gender}' -> '{new_gender}'"
                    ))
                    total_corrected += 1
            else:
                unrecognized.append(f"{p.first_name} {p.last_name}")

        self.stdout.write("\n" + "="*40 + "\n")
        self.stdout.write(self.style.SUCCESS(f"Audit completed!"))
        self.stdout.write(f"Total audited: {total_audited}")
        self.stdout.write(self.style.SUCCESS(f"Total corrected: {total_corrected}"))
        
        if unrecognized:
            self.stdout.write(self.style.WARNING(f"Unrecognized names ({len(unrecognized)}):"))
            for name in unrecognized:
                self.stdout.write(self.style.WARNING(f" - {name}"))
        else:
            self.stdout.write(self.style.SUCCESS("All names recognized and verified successfully!"))
