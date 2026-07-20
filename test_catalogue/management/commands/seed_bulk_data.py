import datetime
import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone

from patients.models import Patient
from encounters.models import Encounter
from test_catalogue.models import TestCategory, Test, TestParameter
from requests.models import TestRequest, RequestedTest
from samples.models import Sample, SampleTrackingLog
from results.models import Result, ParameterResultValue
from billing.models import Invoice, Payment, Receipt
from inventory.models import Supplier, Reagent, StockTransaction
from equipment.models import Equipment, MaintenanceLog
from referrals.models import ReferralPartner, Referral
from quality.models import QCControl, QCRun, NonConformance

User = get_user_model()

FIRST_NAMES = [
    "Kwame", "Abena", "Kofi", "Akua", "Yaw", "Ama", "Kojo", "Efia", "Ebenezer", "Mavis",
    "Edward", "Alice", "Grace", "Samuel", "Daniel", "Emmanuel", "Priscilla", "Gideon",
    "Bernice", "Francis", "Patricia", "Richmond", "Dorothy", "Isaac", "Harriet", "Dennis",
    "Josephine", "Solomon", "Eunice", "Caleb", "Rachel", "Joshua", "Phyllis", "Benjamin"
]

LAST_NAMES = [
    "Mensah", "Osei", "Appiah", "Danso", "Boateng", "Serwaa", "Asante", "Agyeman", "Addo",
    "Asare", "Deva", "Wonderland", "Quaye", "Frimpong", "Owusu", "Amoah", "Kwarteng",
    "Boadu", "Agyei", "Oppong", "Darko", "Antwi", "Acheampong", "Gyamfi", "Tetteh", "Yeboah"
]

STREETS = ["Liberation Road", "Ring Road Central", "Independence Avenue", "Spintex Road", "Cantonments Road", "Osu Badu Street"]
CITIES = ["Accra", "Kumasi", "Takoradi", "Tamale", "Cape Coast", "Tema", "Sunyani", "Koforidua"]
REFERRING_PHYSICIANS = ["Self / Walk-in", "Dr. K. Mensah", "Dr. A. Osei", "Dr. S. Appiah", "Korle-Bu Teaching Hospital", "37 Military Hospital"]

class Command(BaseCommand):
    help = "Seed around 1,000+ realistic records into the LMS database."

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=150,
            help='Number of patients to generate (defaults to 150, generating ~1500 total records across tables).'
        )

    def handle(self, *args, **options):
        num_patients = options['count']
        self.stdout.write(self.style.WARNING(f"Starting bulk data seeding for ~{num_patients} patients and linked records..."))

        # Ensure seed_data has run first
        from django.core.management import call_command
        call_command('seed_data')

        users = list(User.objects.all())
        staff_users = [u for u in users if u.role not in [User.ROLE_PATIENT, User.ROLE_DOCTOR]] or users
        admin_user = staff_users[0] if staff_users else None

        categories = list(TestCategory.objects.all())
        tests = list(Test.objects.all())

        if not tests:
            self.stdout.write(self.style.ERROR("No diagnostic tests found in database. Run seed_data first."))
            return

        # 1. Create Patients
        self.stdout.write("Generating Patients...")
        patient_objs = []
        now = timezone.now()

        for i in range(num_patients):
            fn = random.choice(FIRST_NAMES)
            ln = random.choice(LAST_NAMES)
            dob = datetime.date(random.randint(1955, 2018), random.randint(1, 12), random.randint(1, 28))
            gender = random.choice(['M', 'F'])
            prefix = random.choice(['024', '020', '055', '050', '027'])
            phone = f"{prefix}{random.randint(1000000, 9999999)}"
            email = f"{fn.lower()}.{ln.lower()}{random.randint(10, 99)}@gmail.com"
            address = f"{random.randint(1, 99)} {random.choice(STREETS)}, {random.choice(CITIES)}"

            p = Patient(
                first_name=fn,
                last_name=ln,
                gender=gender,
                date_of_birth=dob,
                phone_number=phone,
                email=email,
                address=address,
                emergency_contact_name=f"{random.choice(FIRST_NAMES)} {ln}",
                emergency_contact_phone=f"024{random.randint(1000000, 9999999)}",
                created_by=admin_user,
                updated_by=admin_user
            )
            patient_objs.append(p)

        Patient.objects.bulk_create(patient_objs)
        created_patients = list(Patient.objects.all().order_by('-id')[:num_patients])
        self.stdout.write(self.style.SUCCESS(f"Created {len(created_patients)} Patients."))

        # 2. Create Encounters & Test Requests
        self.stdout.write("Generating Encounters, Test Requests & Ordered Tests...")
        encounter_types = ['walk_in', 'outpatient', 'inpatient', 'emergency']
        priorities = ['routine', 'urgent', 'stat']

        total_requests = 0
        total_requested_tests = 0
        total_invoices = 0
        total_samples = 0
        total_results = 0

        for patient in created_patients:
            # Each patient has 1-3 visits
            num_visits = random.randint(1, 3)
            for v_idx in range(num_visits):
                days_ago = random.randint(0, 120)
                req_date = now - datetime.timedelta(days=days_ago, hours=random.randint(0, 23))

                enc = Encounter.objects.create(
                    patient=patient,
                    encounter_type=random.choice(encounter_types),
                    referring_physician=random.choice(REFERRING_PHYSICIANS),
                    clinical_notes="Routine medical checkup and diagnostic workup.",
                    created_by=admin_user,
                    updated_by=admin_user
                )
                Encounter.objects.filter(id=enc.id).update(created_at=req_date)

                # Create Test Request
                priority = random.choices(priorities, weights=[70, 20, 10])[0]
                tr = TestRequest.objects.create(
                    encounter=enc,
                    priority=priority,
                    ordered_by=random.choice(staff_users),
                    created_by=admin_user,
                    updated_by=admin_user
                )
                TestRequest.objects.filter(id=tr.id).update(created_at=req_date, request_date=req_date)
                total_requests += 1

                # Select 1 to 4 tests for this request
                selected_tests = random.sample(tests, k=random.randint(1, min(4, len(tests))))
                req_test_objs = []
                for test_obj in selected_tests:
                    rt = RequestedTest.objects.create(
                        request=tr,
                        test=test_obj,
                        price_at_request=test_obj.price,
                        status=random.choice(['pending', 'collected', 'received', 'completed', 'verified']),
                        created_by=admin_user,
                        updated_by=admin_user
                    )
                    req_test_objs.append(rt)
                    total_requested_tests += 1

                # Auto-Create / Update Invoice
                inv, _ = Invoice.objects.get_or_create(
                    request=tr,
                    defaults={'patient': patient, 'created_by': admin_user, 'updated_by': admin_user}
                )
                inv.calculate_totals()
                
                # Payment status simulation
                pay_status = random.choices(['paid', 'unpaid', 'partial'], weights=[60, 25, 15])[0]
                if pay_status == 'paid':
                    inv.paid_amount = inv.payable_amount
                    inv.balance_due = Decimal('0.00')
                    inv.payment_status = Invoice.STATUS_PAID
                    tr.payment_status = TestRequest.PAYMENT_PAID
                elif pay_status == 'partial':
                    inv.paid_amount = (inv.payable_amount / Decimal('2.0')).quantize(Decimal('0.01'))
                    inv.balance_due = inv.payable_amount - inv.paid_amount
                    inv.payment_status = Invoice.STATUS_PARTIAL
                    tr.payment_status = TestRequest.PAYMENT_PARTIAL
                else:
                    inv.paid_amount = Decimal('0.00')
                    inv.balance_due = inv.payable_amount
                    inv.payment_status = Invoice.STATUS_UNPAID
                    tr.payment_status = TestRequest.PAYMENT_UNPAID

                inv.save()
                tr.save()
                total_invoices += 1

                # Create Payment & Receipt record if paid or partial
                if inv.paid_amount > 0:
                    pmt = Payment.objects.create(
                        invoice=inv,
                        amount_paid=inv.paid_amount,
                        payment_method=random.choice(['cash', 'mobile_money', 'card', 'insurance']),
                        transaction_reference=f"TXN-{random.randint(100000, 999999)}",
                        received_by=random.choice(staff_users),
                        created_by=admin_user,
                        updated_by=admin_user
                    )
                    Receipt.objects.create(
                        payment=pmt,
                        created_by=admin_user,
                        updated_by=admin_user
                    )

                # Process Samples & Results for collected/received/completed requested tests
                for rt in req_test_objs:
                    if rt.status in ['collected', 'received', 'completed', 'verified']:
                        sample = Sample.objects.create(
                            request=tr,
                            sample_type=rt.test.sample_type or 'Serum',
                            barcode_number=f"SMP{random.randint(1000000, 9999999)}",
                            collected_at=req_date + datetime.timedelta(minutes=30),
                            collected_by=random.choice(staff_users),
                            status='received' if rt.status in ['received', 'completed', 'verified'] else 'collected',
                            created_by=admin_user,
                            updated_by=admin_user
                        )
                        total_samples += 1

                        SampleTrackingLog.objects.create(
                            sample=sample,
                            status_to=sample.status,
                            notes=f"Sample transitioned to {sample.status}",
                            scanned_by=random.choice(staff_users),
                            created_by=admin_user,
                            updated_by=admin_user
                        )

                        if rt.status in ['completed', 'verified']:
                            res = Result.objects.create(
                                requested_test=rt,
                                sample=sample,
                                value="Normal Findings" if rt.status == 'verified' else "Automated Run",
                                interpretation="Investigation completed cleanly.",
                                status='verified' if rt.status == 'verified' else 'draft',
                                verified_by=random.choice(staff_users) if rt.status == 'verified' else None,
                                verified_at=req_date + datetime.timedelta(hours=2) if rt.status == 'verified' else None,
                                recorded_by=random.choice(staff_users),
                                created_by=admin_user,
                                updated_by=admin_user
                            )
                            total_results += 1

                            # Populate parameter result values if sub-parameters exist
                            params = list(rt.test.parameters.all())
                            for p in params:
                                val_str = f"{random.uniform(5.0, 95.0):.1f}"
                                flag = random.choices(['N', 'H', 'L'], weights=[80, 10, 10])[0]
                                ParameterResultValue.objects.create(
                                    result=res,
                                    parameter=p,
                                    value=val_str,
                                    flag=flag,
                                    created_by=admin_user,
                                    updated_by=admin_user
                                )

        # 3. Seed Suppliers & Reagents Stock Transactions
        self.stdout.write("Generating Inventory & Stock Transactions...")
        reagents = list(Reagent.objects.all())
        for rgt in reagents:
            for _ in range(random.randint(2, 5)):
                tx_type = random.choice(['receive', 'issue', 'adjust'])
                qty = random.randint(5, 50)
                StockTransaction.objects.create(
                    reagent=rgt,
                    transaction_type=tx_type,
                    quantity=qty,
                    notes=f"Bulk seed transaction: {tx_type}",
                    created_by=admin_user,
                    updated_by=admin_user
                )

        # 4. Seed Equipment Maintenance & Quality Control Runs
        self.stdout.write("Generating Equipment Maintenance & QC Runs...")
        equipments = list(Equipment.objects.all())
        for eq in equipments:
            for _ in range(3):
                MaintenanceLog.objects.create(
                    equipment=eq,
                    maintenance_type=random.choice(['calibration', 'preventive', 'repair']),
                    performed_by_name=random.choice(staff_users).get_full_name() or "Technician Engineer",
                    notes="Automated diagnostic calibration and sensor check.",
                    start_date=now - datetime.timedelta(days=random.randint(1, 60)),
                    created_by=admin_user,
                    updated_by=admin_user
                )

        qc_controls = list(QCControl.objects.all())
        for qc in qc_controls:
            for _ in range(3):
                QCRun.objects.create(
                    control=qc,
                    value=f"{random.uniform(1.0, 10.0):.2f}",
                    status=random.choice(['pass', 'fail']),
                    notes="Daily automated quality control run.",
                    created_by=admin_user,
                    updated_by=admin_user
                )

        # Summary Statistics
        self.stdout.write(self.style.SUCCESS("\n" + "=" * 60))
        self.stdout.write(self.style.SUCCESS("  BULK SEEDING COMPLETED SUCCESSFULLY!"))
        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write(f"- Patients Generated:        {len(created_patients)}")
        self.stdout.write(f"- Encounters Generated:      {total_requests}")
        self.stdout.write(f"- Test Requests Generated:   {total_requests}")
        self.stdout.write(f"- Requested Tests Generated: {total_requested_tests}")
        self.stdout.write(f"- Invoices Generated:        {total_invoices}")
        self.stdout.write(f"- Samples Generated:         {total_samples}")
        self.stdout.write(f"- Results Generated:         {total_results}")
        self.stdout.write(self.style.SUCCESS("TOTAL DATABASE RECORDS GENERATED: ~1,500+ records!\n"))
