from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Invoice, Payment, Receipt
from .serializers import InvoiceSerializer, PaymentSerializer, ReceiptSerializer

class InvoiceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        payment = serializer.save(
            received_by=self.request.user,
            created_by=self.request.user,
            updated_by=self.request.user
        )
        
        # Create Receipt automatically
        Receipt.objects.create(
            payment=payment,
            created_by=self.request.user,
            updated_by=self.request.user
        )

class ReceiptViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Receipt.objects.all()
    serializer_class = ReceiptSerializer
    permission_classes = [permissions.IsAuthenticated]
