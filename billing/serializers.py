from rest_framework import serializers
from .models import Invoice, Payment, Receipt
from patients.serializers import PatientSerializer
from requests.serializers import TestRequestSerializer

class InvoiceSerializer(serializers.ModelSerializer):
    patient_detail = PatientSerializer(source='patient', read_only=True)
    request_detail = TestRequestSerializer(source='request', read_only=True)

    class Meta:
        model = Invoice
        fields = '__all__'
        read_only_fields = ['id', 'uuid', 'created_at', 'updated_at', 'created_by', 'updated_by', 'is_deleted', 'total_amount', 'payable_amount', 'paid_amount', 'balance_due', 'payment_status']

class PaymentSerializer(serializers.ModelSerializer):
    received_by_name = serializers.CharField(source='received_by.username', read_only=True)

    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ['id', 'uuid', 'created_at', 'updated_at', 'created_by', 'updated_by', 'is_deleted', 'payment_date', 'received_by']

class ReceiptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receipt
        fields = '__all__'
        read_only_fields = ['id', 'uuid', 'created_at', 'updated_at', 'created_by', 'updated_by', 'is_deleted', 'receipt_number', 'issued_at']
