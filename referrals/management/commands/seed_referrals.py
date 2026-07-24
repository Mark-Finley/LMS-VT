import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from django.core.management import call_command

from referrals.models import ReferralPartner, Referral
from requests.models import RequestedTest
from patients.models import Patient
from encounters.models import Encounter
from requests.models import TestRequest
from test_catalogue.models import Test

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds referral partners and corresponding referral cases'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Checking for admin user...")
        admin_user = User.objects.filter(role=User.ROLE_ADMINISTRATOR).first()
        if not admin_user:
            admin_user = User.objects.first()

        self.stdout.write("Seeding Referral Partners...")
        partners_data = [
            {
                'name': 'St. Jude Reference Laboratory',
                'contact_number': '+1 555-9302',
                'email': 'referrals@stjude.org',
                'address': '456 Medical Parkway, Memphis'
            },
            {
                'name': 'Metropolis Clinical Laboratories',
                'contact_number': '+1 555-4920',
                'email': 'partner@metropolis.com',
                'address': '789 Diagnostics Blvd, Metropolis'
            },
            {
                'name': 'Synlab International',
                'contact_number': '+233 24 123 4567',
                'email': 'info.ghana@synlab.com',
                'address': '12 Ring Road East, Accra'
            },
            {
                'name': 'Lancet Laboratories',
                'contact_number': '+233 30 261 0480',
                'email': 'referrals@lancet.com.gh',
                'address': '34 Kojo Thompson Rd, Adabraka, Accra'
            },
        ]

        partners = []
        for p_data in partners_data:
            partner, created = ReferralPartner.objects.get_or_create(
                name=p_data['name'],
                defaults={
                    'contact_number': p_data['contact_number'],
                    'email': p_data['email'],
                    'address': p_data['address'],
                    'created_by': admin_user,
                    'updated_by': admin_user,
                    'status': 'active'
                }
            )
            partners.append(partner)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created partner: {partner.name}"))
            else:
                self.stdout.write(f"Partner already exists: {partner.name}")

        self.stdout.write("Checking for existing requested tests...")
        requested_tests = list(RequestedTest.objects.all())
        
        # If there are no requested tests in the database, let's create a few dummy ones
        if not requested_tests:
            self.stdout.write(self.style.WARNING("No requested tests found. Creating demo patients and requests to link referrals..."))
            
            # Ensure we have tests first
            if not Test.objects.exists():
                call_command('seed_data')
            
            tests = list(Test.objects.all())
            if not tests:
                self.stdout.write(self.style.ERROR("No diagnostic tests available. Cannot seed referrals."))
                return

            # Create a test patient
            patient = Patient.objects.create(
                first_name="Referral",
                last_name="Demo",
                gender="M",
                date_of_birth="1990-01-01",
                phone_number="0240000000",
                created_by=admin_user,
                updated_by=admin_user
            )

            # Create encounter
            encounter = Encounter.objects.create(
                patient=patient,
                encounter_type="walk_in",
                referring_physician="Dr. External Partner",
                created_by=admin_user,
                updated_by=admin_user
            )

            # Create test request
            tr = TestRequest.objects.create(
                encounter=encounter,
                ordered_by=admin_user,
                created_by=admin_user,
                updated_by=admin_user
            )

            # Link requested tests
            for test_obj in random.sample(tests, min(3, len(tests))):
                rt = RequestedTest.objects.create(
                    request=tr,
                    test=test_obj,
                    price_at_request=test_obj.price,
                    status='pending',
                    created_by=admin_user,
                    updated_by=admin_user
                )
                requested_tests.append(rt)

        self.stdout.write(f"Seeding referral cases for {min(len(requested_tests), 20)} tests...")
        
        # Select up to 20 requested tests to associate with referrals
        selected_tests = random.sample(requested_tests, min(len(requested_tests), 20))
        
        referral_types = [Referral.TYPE_INCOMING, Referral.TYPE_OUTGOING]
        statuses = [Referral.STATUS_PENDING, Referral.STATUS_SENT, Referral.STATUS_RECEIVED, Referral.STATUS_COMPLETED]
        
        referral_notes = {
            Referral.TYPE_INCOMING: [
                "Sample received from partner clinic for advanced analysis.",
                "Inbound referral for specialized biochemistry profiling.",
                "Partner requested PCR confirmation for this sample.",
                "Specialized diagnostic request forwarded by partner hospital."
            ],
            Referral.TYPE_OUTGOING: [
                "Sample dispatched to partner laboratory due to analyzer downtime.",
                "Outbound referral for rare genetic screening not performed in-house.",
                "Specimen sent for confirmation assay.",
                "Referred to reference laboratory for toxicological screening."
            ]
        }

        created_count = 0
        for rt in selected_tests:
            # Avoid duplicate referrals for the same requested test
            if Referral.objects.filter(requested_test=rt).exists():
                continue
                
            ref_type = random.choice(referral_types)
            status = random.choice(statuses)
            partner = random.choice(partners)
            notes = random.choice(referral_notes[ref_type])
            
            Referral.objects.create(
                requested_test=rt,
                partner=partner,
                referral_type=ref_type,
                status=status,
                notes=notes,
                created_by=admin_user,
                updated_by=admin_user
            )
            created_count += 1
            self.stdout.write(self.style.SUCCESS(f"Created {ref_type} referral to {partner.name} for test: {rt.test.name} (Status: {status})"))

        self.stdout.write(self.style.SUCCESS(f"Successfully seeded {created_count} referral cases."))
