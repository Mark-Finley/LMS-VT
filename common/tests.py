from django.test import TestCase
from django.contrib.auth import get_user_model
from inventory.models import Supplier, Reagent, StockTransaction
from equipment.models import Equipment, MaintenanceLog
from quality.models import QCControl, QCRun, NonConformance
from referrals.models import ReferralPartner, Referral
from requests.models import TestRequest, RequestedTest
from test_catalogue.models import TestCategory, Test
from encounters.models import Encounter
from patients.models import Patient
from common.notifications import send_notification
import datetime

User = get_user_model()

class Phase2LMSWorkflowTestCase(TestCase):
    def setUp(self):
        # Setup base user
        self.user = User.objects.create_user(
            username='lab_user',
            password='Password123!',
            role=User.ROLE_LAB_TECHNICIAN
        )

        # Setup base patient and requested test for referral testing
        self.patient = Patient.objects.create(
            first_name='Alice',
            last_name='Wonder',
            gender='F',
            date_of_birth='1995-10-10'
        )
        self.encounter = Encounter.objects.create(
            patient=self.patient,
            encounter_type='walk_in'
        )
        self.category = TestCategory.objects.create(name='Test Cat')
        self.test = Test.objects.create(
            category=self.category,
            name='Special Referral Test',
            code='SRT',
            price=150.00,
            turnaround_time_hours=24,
            sample_type='Serum'
        )
        self.test_request = TestRequest.objects.create(
            encounter=self.encounter,
            ordered_by=self.user
        )
        self.requested_test = RequestedTest.objects.create(
            request=self.test_request,
            test=self.test
        )

    def test_inventory_stock_logic(self):
        # 1. Create Supplier
        supplier = Supplier.objects.create(name='Acme Corp')
        
        # 2. Create Reagent
        reagent = Reagent.objects.create(
            name='Hemoglobin Lyser',
            code='HEM-LYSE',
            unit='Vial',
            min_stock_level=5.00,
            current_quantity=10.00,
            supplier=supplier
        )
        self.assertEqual(reagent.current_quantity, 10.00)

        # 3. Create stock transactions (receive stock)
        StockTransaction.objects.create(
            reagent=reagent,
            transaction_type=StockTransaction.TYPE_RECEIVE,
            quantity=5.00,
            created_by=self.user
        )
        reagent.refresh_from_db()
        self.assertEqual(reagent.current_quantity, 15.00)

        # 4. Issue stock (deduct stock)
        StockTransaction.objects.create(
            reagent=reagent,
            transaction_type=StockTransaction.TYPE_ISSUE,
            quantity=3.00,
            created_by=self.user
        )
        reagent.refresh_from_db()
        self.assertEqual(reagent.current_quantity, 12.00)

    def test_equipment_calibration_triggers(self):
        # 1. Create Equipment
        eq = Equipment.objects.create(
            name='Roche Centrifuge',
            model='Centri-X',
            serial_number='SN-99402',
            manufacturer='Roche',
            status=Equipment.STATUS_ACTIVE
        )
        self.assertIsNone(eq.last_calibration_date)

        # 2. Perform a calibration maintenance run
        now = datetime.datetime.now(datetime.timezone.utc)
        MaintenanceLog.objects.create(
            equipment=eq,
            maintenance_type=MaintenanceLog.TYPE_CALIBRATION,
            performed_by_name='John Engineer',
            start_date=now,
            end_date=now,
            created_by=self.user
        )
        eq.refresh_from_db()
        self.assertEqual(eq.last_calibration_date, now.date())
        self.assertIsNotNone(eq.next_calibration_date)

    def test_quality_control_logs(self):
        # 1. Create QC Control lot
        qc = QCControl.objects.create(
            name='Lipid Normal Control',
            lot_number='LOT-LIP-N1',
            expiry_date='2027-12-31',
            target_value='150.00',
            standard_deviation=5.00
        )
        
        # 2. Add a QC Run
        run = QCRun.objects.create(
            control=qc,
            value='149.50',
            status=QCRun.STATUS_PASS,
            created_by=self.user
        )
        self.assertEqual(run.status, QCRun.STATUS_PASS)

        # 3. Log a non-conformance event
        nc = NonConformance.objects.create(
            title='Sample clotted',
            description='CBC sample was received clotted and rejected.',
            date_identified='2026-07-18',
            corrective_action='Request recollection.',
            status=NonConformance.STATUS_CLOSED,
            created_by=self.user
        )
        self.assertEqual(nc.status, NonConformance.STATUS_CLOSED)

    def test_referrals_and_partners(self):
        # 1. Create Partner
        partner = ReferralPartner.objects.create(name='Mayo Clinic Labs')

        # 2. Register referral case
        ref = Referral.objects.create(
            requested_test=self.requested_test,
            partner=partner,
            referral_type=Referral.TYPE_OUTGOING,
            status=Referral.STATUS_SENT,
            created_by=self.user
        )
        self.assertEqual(ref.status, Referral.STATUS_SENT)

    def test_notifications_dispatch(self):
        # Dispatch notification
        log = send_notification(
            recipient_name='Patient Alice',
            recipient_contact='alice@wonderland.com',
            notification_type='email',
            message='Your results are ready.',
            subject='Medical Report Update'
        )
        self.assertTrue(log.is_sent)
        self.assertEqual(log.recipient_name, 'Patient Alice')

    def test_doctor_and_patient_portal_apis(self):
        from django.urls import reverse
        from django.test import Client
        import json
        
        client = Client()

        # 1. Test Doctor endpoints with Doctor User
        doctor_user = User.objects.create_user(
            username='doctor_jones',
            password='Password123!',
            role=User.ROLE_DOCTOR,
            first_name='Indiana',
            last_name='Jones'
        )
        client.force_login(doctor_user)

        # Retrieve Doctor requests list
        url = reverse('doctor-requests')
        response = client.get(url)
        self.assertEqual(response.status_code, 200)

        # Create Test Request as Doctor
        create_url = reverse('doctor-create-request')
        response = client.post(create_url, json.dumps({
            'encounter': self.encounter.id,
            'test_ids': [self.test.id],
            'priority': 'urgent'
        }), content_type='application/json')
        self.assertEqual(response.status_code, 201)

        # 2. Test Patient endpoints with Patient User
        patient_user = User.objects.create_user(
            username='patient_alice',
            password='Password123!',
            role=User.ROLE_PATIENT,
            patient=self.patient
        )
        client.force_login(patient_user)

        # Get mobile profile
        profile_url = reverse('mobile-profile')
        response = client.get(profile_url)
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertEqual(data['first_name'], 'Alice')

        # Get results
        results_url = reverse('mobile-results')
        response = client.get(results_url)
        self.assertEqual(response.status_code, 200)

    def test_test_parameter_creation_and_results_entry(self):
        from test_catalogue.models import TestParameter
        from results.models import Result, ParameterResultValue
        from samples.models import Sample
        
        # 1. Create a Test Parameter
        param = TestParameter.objects.create(
            test=self.test,
            name='Segmented Neutrophils',
            normal_range='40 - 70',
            units='%'
        )
        self.assertEqual(param.name, 'Segmented Neutrophils')
        
        # Create Sample
        sample = Sample.objects.create(
            request=self.test_request,
            sample_type='Serum',
            barcode_number='SMP100234',
            collected_by=self.user
        )
        
        # 2. Record dynamic parameter result value
        result = Result.objects.create(
            requested_test=self.requested_test,
            sample=sample,
            value='Multi-parameter'
        )
        pv = ParameterResultValue.objects.create(
            result=result,
            parameter=param,
            value='45.5',
            flag='N'
        )
        self.assertEqual(pv.value, '45.5')
        self.assertEqual(pv.flag, 'N')
        self.assertEqual(result.parameter_values.count(), 1)

    def test_delete_requested_test_invoice_recalculation(self):
        from billing.models import Invoice
        
        # 1. Create Invoice manually for the test request (since setUp used ORM create bypassing serializer)
        invoice = Invoice.objects.create(
            request=self.test_request,
            patient=self.patient,
            created_by=self.user,
            updated_by=self.user
        )
        invoice.save()
        self.assertEqual(invoice.total_amount, 150.00)
        
        # 2. Add another test
        test2 = Test.objects.create(
            category=self.category,
            name='Second Test',
            code='ST2',
            price=50.00,
            turnaround_time_hours=12,
            sample_type='Urine'
        )
        
        from django.test import Client
        import json
        client = Client()
        client.force_login(self.user)
        
        from django.urls import reverse
        add_url = reverse('requested-tests-list')
        response = client.post(add_url, json.dumps({
            'request': self.test_request.id,
            'test': test2.id
        }), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        
        # Verify invoice total updated
        invoice.refresh_from_db()
        self.assertEqual(invoice.total_amount, 200.00)
        
        # 3. Now delete the test via API client
        created_rt_id = response.data['id']
        delete_url = reverse('requested-tests-detail', args=[created_rt_id])
        response = client.delete(delete_url)
        self.assertEqual(response.status_code, 204)
        
        # Verify invoice total updated back to 150.00
        invoice.refresh_from_db()
        self.assertEqual(invoice.total_amount, 150.00)

