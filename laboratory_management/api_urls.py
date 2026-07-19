from django.urls import path, include
from rest_framework.routers import DefaultRouter
from accounts.views import obtain_jwt_token
from patients.views import PatientViewSet
from encounters.views import EncounterViewSet
from test_catalogue.views import TestCategoryViewSet, TestViewSet, TestParameterViewSet
from requests.views import TestRequestViewSet, RequestedTestViewSet
from samples.views import SampleViewSet, SampleTrackingLogViewSet
from results.views import ResultViewSet
from billing.views import InvoiceViewSet, PaymentViewSet, ReceiptViewSet

router = DefaultRouter()
router.register(r'patients', PatientViewSet, basename='patients')
router.register(r'encounters', EncounterViewSet, basename='encounters')
router.register(r'test-categories', TestCategoryViewSet, basename='test-categories')
router.register(r'tests', TestViewSet, basename='tests')
router.register(r'test-parameters', TestParameterViewSet, basename='test-parameters')
router.register(r'test-requests', TestRequestViewSet, basename='test-requests')
router.register(r'requested-tests', RequestedTestViewSet, basename='requested-tests')
router.register(r'samples', SampleViewSet, basename='samples')
router.register(r'sample-tracking', SampleTrackingLogViewSet, basename='sample-tracking')
router.register(r'results', ResultViewSet, basename='results')
router.register(r'invoices', InvoiceViewSet, basename='invoices')
router.register(r'payments', PaymentViewSet, basename='payments')
router.register(r'receipts', ReceiptViewSet, basename='receipts')

# Phase 2 REST Viewsets
from inventory.views import SupplierViewSet, ReagentViewSet, StockTransactionViewSet
from equipment.views import EquipmentViewSet, MaintenanceLogViewSet
from referrals.views import ReferralPartnerViewSet, ReferralViewSet
from quality.views import QCControlViewSet, QCRunViewSet, NonConformanceViewSet

router.register(r'suppliers', SupplierViewSet, basename='suppliers')
router.register(r'reagents', ReagentViewSet, basename='reagents')
router.register(r'stock-transactions', StockTransactionViewSet, basename='stock-transactions')
router.register(r'equipment', EquipmentViewSet, basename='equipment')
router.register(r'maintenance-logs', MaintenanceLogViewSet, basename='maintenance-logs')
router.register(r'referral-partners', ReferralPartnerViewSet, basename='referral-partners')
router.register(r'referrals', ReferralViewSet, basename='referrals')
router.register(r'qc-controls', QCControlViewSet, basename='qc-controls')
router.register(r'qc-runs', QCRunViewSet, basename='qc-runs')
router.register(r'non-conformances', NonConformanceViewSet, basename='non-conformances')

from dashboard.views import DashboardMetricsView
from dashboard.mobile_views import MobilePatientProfileView, MobilePatientResultsView, MobilePatientInvoicesView
from dashboard.doctor_views import DoctorRequestListView, DoctorCreateRequestView

urlpatterns = [
    path('auth/token/', obtain_jwt_token, name='token_obtain_pair'),
    path('dashboard/metrics/', DashboardMetricsView.as_view(), name='dashboard-metrics'),
    
    # Mobile Patient Portal endpoints
    path('mobile/profile/', MobilePatientProfileView.as_view(), name='mobile-profile'),
    path('mobile/results/', MobilePatientResultsView.as_view(), name='mobile-results'),
    path('mobile/invoices/', MobilePatientInvoicesView.as_view(), name='mobile-invoices'),

    # Doctor Portal endpoints
    path('doctor/requests/', DoctorRequestListView.as_view(), name='doctor-requests'),
    path('doctor/create-request/', DoctorCreateRequestView.as_view(), name='doctor-create-request'),

    path('', include(router.urls)),
]
