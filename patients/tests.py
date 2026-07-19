from django.test import TestCase
from django.contrib.auth import get_user_model
from patients.models import Patient
from encounters.models import Encounter
from test_catalogue.models import TestCategory, Test
from requests.models import TestRequest, RequestedTest
from billing.models import Invoice

User = get_user_model()

class LMSWorkflowTestCase(TestCase):
    def setUp(self):
        # Create standard user accounts
        self.receptionist = User.objects.create_user(
            username='recep_test',
            password='Password123!',
            role=User.ROLE_RECEPTIONIST
        )
        
        # Create categories and tests
        self.category = TestCategory.objects.create(
            name='Hematology',
            description='Blood tests'
        )
        self.cbc = Test.objects.create(
            category=self.category,
            name='Complete Blood Count',
            code='CBC',
            price=45.00,
            turnaround_time_hours=4,
            normal_range='12-16',
            sample_type='Whole Blood (EDTA)'
        )

    def test_complete_registration_and_billing_workflow(self):
        # 1. Create Patient
        patient = Patient.objects.create(
            first_name='John',
            last_name='Doe',
            gender='M',
            date_of_birth='1990-05-15',
            phone_number='1234567890',
            created_by=self.receptionist
        )
        self.assertEqual(patient.full_name, 'John Doe')
        
        # 2. Create Encounter
        encounter = Encounter.objects.create(
            patient=patient,
            encounter_type=Encounter.TYPE_WALKIN,
            referring_physician='Dr. Smith',
            created_by=self.receptionist
        )
        self.assertEqual(encounter.patient, patient)
        
        # 3. Create Test Request and select CBC test
        request = TestRequest.objects.create(
            encounter=encounter,
            priority=TestRequest.PRIORITY_ROUTINE,
            ordered_by=self.receptionist,
            created_by=self.receptionist
        )
        self.assertTrue(request.request_number.startswith('REQ-'))
        
        # Add requested test
        req_test = RequestedTest.objects.create(
            request=request,
            test=self.cbc,
            price_at_request=self.cbc.price,
            created_by=self.receptionist
        )
        
        # Create Invoice linked to request
        invoice = Invoice.objects.create(
            request=request,
            patient=patient,
            created_by=self.receptionist
        )
        
        # 4. Verify automated billing calculation
        self.assertEqual(invoice.total_amount, 45.00)
        self.assertEqual(invoice.payable_amount, 45.00)
        self.assertEqual(invoice.balance_due, 45.00)
        self.assertEqual(invoice.payment_status, Invoice.STATUS_UNPAID)
