from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from patients.serializers import PatientSerializer
from results.serializers import ResultSerializer
from results.models import Result
from billing.models import Invoice
from billing.serializers import InvoiceSerializer

class MobilePatientProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        patient = request.user.patient
        if not patient:
            return Response(
                {"detail": "Logged-in user is not associated with a patient record."},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = PatientSerializer(patient)
        return Response(serializer.data)

class MobilePatientResultsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        patient = request.user.patient
        if not patient:
            return Response(
                {"detail": "Logged-in user is not associated with a patient record."},
                status=status.HTTP_400_BAD_REQUEST
            )
        results = Result.objects.filter(
            requested_test__request__encounter__patient=patient,
            status__in=['verified', 'released']
        )
        serializer = ResultSerializer(results, many=True)
        return Response(serializer.data)

class MobilePatientInvoicesView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        patient = request.user.patient
        if not patient:
            return Response(
                {"detail": "Logged-in user is not associated with a patient record."},
                status=status.HTTP_400_BAD_REQUEST
            )
        invoices = Invoice.objects.filter(patient=patient)
        serializer = InvoiceSerializer(invoices, many=True)
        return Response(serializer.data)
