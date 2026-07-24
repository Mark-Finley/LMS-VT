from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Invoice, Payment, Receipt
from .serializers import InvoiceSerializer, PaymentSerializer, ReceiptSerializer

from django.db.models import Q
from common.pagination import StandardResultsSetPagination

class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get('search')
        if search:
            words = search.split()
            q_obj = Q()
            for word in words:
                q_obj &= (
                    Q(patient__first_name__icontains=word) |
                    Q(patient__last_name__icontains=word) |
                    Q(patient__phone_number__icontains=word) |
                    Q(id__icontains=word)
                )
            queryset = queryset.filter(q_obj)
        return queryset.order_by('-created_at')

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
