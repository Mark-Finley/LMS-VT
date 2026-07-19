from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Result
from .serializers import ResultSerializer
from requests.models import RequestedTest

class ResultViewSet(viewsets.ModelViewSet):
    queryset = Result.objects.all()
    serializer_class = ResultSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Parse numeric value if possible
        value = serializer.validated_data.get('value', '')
        value_numeric = None
        try:
            value_numeric = float(value)
        except ValueError:
            pass

        result = serializer.save(
            recorded_by=self.request.user,
            recorded_at=timezone.now(),
            created_by=self.request.user,
            updated_by=self.request.user,
            status=Result.STATUS_DRAFT,
            value_numeric=value_numeric
        )
        
        # Update RequestedTest status to COMPLETED (meaning result entered)
        req_test = result.requested_test
        req_test.status = RequestedTest.STATUS_COMPLETED
        req_test.save()

    @action(detail=True, methods=['post'])
    def review(self, request, pk=None):
        result = self.get_object()
        result.status = Result.STATUS_REVIEWED
        result.reviewed_by = request.user
        result.reviewed_at = timezone.now()
        result.save(update_fields=['status', 'reviewed_by', 'reviewed_at'])
        return Response({'status': 'result reviewed'})

    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        result = self.get_object()
        
        # Verify permissions: must be pathologist or admin or lab manager
        if request.user.role not in ['pathologist', 'administrator', 'laboratory_manager']:
            return Response({'error': 'Only Pathologists or Managers can verify results'}, status=status.HTTP_403_FORBIDDEN)
            
        result.status = Result.STATUS_VERIFIED
        result.verified_by = request.user
        result.verified_at = timezone.now()
        result.electronic_signature = f"Signed digitally by Pathologist {request.user.get_full_name()} (ID: {request.user.id})"
        result.save(update_fields=['status', 'verified_by', 'verified_at', 'electronic_signature'])
        
        # Update RequestedTest status to VERIFIED
        req_test = result.requested_test
        req_test.status = RequestedTest.STATUS_VERIFIED
        req_test.save()
        
        return Response({'status': 'result verified', 'signed_by': request.user.get_full_name()})

    @action(detail=True, methods=['post'])
    def release(self, request, pk=None):
        result = self.get_object()
        
        if result.status != Result.STATUS_VERIFIED:
            return Response({'error': 'Result must be verified before release'}, status=status.HTTP_400_BAD_REQUEST)
            
        result.status = Result.STATUS_RELEASED
        result.save(update_fields=['status'])
        
        # Update RequestedTest status to RELEASED
        req_test = result.requested_test
        req_test.status = RequestedTest.STATUS_RELEASED
        req_test.save()
        
        return Response({'status': 'result released'})
