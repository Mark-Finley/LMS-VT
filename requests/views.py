from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from django.http import HttpResponse
from .models import TestRequest, RequestedTest
from .serializers import TestRequestSerializer, RequestedTestSerializer

class TestRequestViewSet(viewsets.ModelViewSet):
    queryset = TestRequest.objects.all()
    serializer_class = TestRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    @action(detail=True, methods=['get'])
    def download_pdf(self, request, pk=None):
        from results.reports import generate_patient_report
        test_request = self.get_object()
        pdf_buffer = generate_patient_report(test_request)
        response = HttpResponse(pdf_buffer.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Report_{test_request.request_number}.pdf"'
        return response

class RequestedTestViewSet(viewsets.ModelViewSet):
    queryset = RequestedTest.objects.all()
    serializer_class = RequestedTestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
