# pyrefly: ignore [missing-import]
from rest_framework import viewsets, permissions, status
# pyrefly: ignore [missing-import]
from rest_framework.decorators import action
# pyrefly: ignore [missing-import]
from rest_framework.response import Response
from django.utils import timezone
from .models import Sample, SampleTrackingLog
from .serializers import SampleSerializer, SampleTrackingLogSerializer
from requests.models import RequestedTest

class SampleViewSet(viewsets.ModelViewSet):
    queryset = Sample.objects.all()
    serializer_class = SampleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        sample = serializer.save(
            collected_by=self.request.user,
            collected_at=timezone.now(),
            created_by=self.request.user,
            updated_by=self.request.user
        )
        # Log initial collection
        SampleTrackingLog.objects.create(
            sample=sample,
            scanned_by=self.request.user,
            status_to=Sample.STATUS_COLLECTED,
            notes='Specimen collected from patient'
        )
        # Update corresponding requested tests to 'collected'
        # We can map sample_type to requested tests
        # For simplicity, let's update all 'pending' tests in this request to 'collected'
        requested_tests = sample.request.requested_tests.filter(status=RequestedTest.STATUS_PENDING)
        for rt in requested_tests:
            # Check if sample type matches
            if rt.test.sample_type.lower() == sample.sample_type.lower():
                rt.status = RequestedTest.STATUS_COLLECTED
                rt.save()

    @action(detail=True, methods=['post'])
    def receive(self, request, pk=None):
        sample = self.get_object()
        sample.status = Sample.STATUS_RECEIVED
        sample.received_by = request.user
        sample.received_at = timezone.now()
        sample.save(update_fields=['status', 'received_by', 'received_at'])
        
        # Log tracking scan
        SampleTrackingLog.objects.create(
            sample=sample,
            scanned_by=request.user,
            status_to=Sample.STATUS_RECEIVED,
            notes=request.data.get('notes', 'Sample received in laboratory')
        )
        
        # Update requested tests that are collected to 'received'
        requested_tests = sample.request.requested_tests.filter(status=RequestedTest.STATUS_COLLECTED)
        for rt in requested_tests:
            if rt.test.sample_type.lower() == sample.sample_type.lower():
                rt.status = RequestedTest.STATUS_RECEIVED
                rt.save()

        return Response({'status': 'sample received', 'barcode_number': sample.barcode_number})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        sample = self.get_object()
        reason = request.data.get('rejection_reason', 'Unspecified reason')
        sample.status = Sample.STATUS_REJECTED
        sample.rejection_reason = reason
        sample.save(update_fields=['status', 'rejection_reason'])

        # Log rejection
        SampleTrackingLog.objects.create(
            sample=sample,
            scanned_by=request.user,
            status_to=Sample.STATUS_REJECTED,
            notes=f'Sample rejected: {reason}'
        )

        # Update requested tests to 'rejected'
        requested_tests = sample.request.requested_tests.all()
        for rt in requested_tests:
            if rt.test.sample_type.lower() == sample.sample_type.lower():
                rt.status = RequestedTest.STATUS_REJECTED
                rt.save()

        return Response({'status': 'sample rejected', 'rejection_reason': reason})

    @action(detail=False, methods=['get'], url_path='specimen-types')
    def specimen_types(self, request):
        default_types = [
            'Whole Blood', 'Serum', 'Plasma', 'Urine', 'Stool',
            'CSF', 'Sputum', 'Semen', 'Skin Scraping', 'Skin Snip',
            'High Vaginal Swab', 'Fluoride Blood'
        ]
        db_types = Sample.objects.values_list('sample_type', flat=True).distinct()
        combined = list(default_types)
        lower_defaults = {t.lower() for t in default_types}
        for t in db_types:
            if t and t.strip() and t.lower() not in lower_defaults:
                combined.append(t.strip())
        return Response(combined)

class SampleTrackingLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SampleTrackingLog.objects.all()
    serializer_class = SampleTrackingLogSerializer
    permission_classes = [permissions.IsAuthenticated]
