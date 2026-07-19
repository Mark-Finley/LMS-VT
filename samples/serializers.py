from rest_framework import serializers
from .models import Sample, SampleTrackingLog
from requests.serializers import TestRequestSerializer

class SampleSerializer(serializers.ModelSerializer):
    request_detail = TestRequestSerializer(source='request', read_only=True)
    collected_by_name = serializers.CharField(source='collected_by.username', read_only=True)
    received_by_name = serializers.CharField(source='received_by.username', read_only=True)

    class Meta:
        model = Sample
        fields = '__all__'
        read_only_fields = ['id', 'uuid', 'created_at', 'updated_at', 'created_by', 'updated_by', 'is_deleted', 'barcode_number']

class SampleTrackingLogSerializer(serializers.ModelSerializer):
    scanned_by_username = serializers.CharField(source='scanned_by.username', read_only=True)

    class Meta:
        model = SampleTrackingLog
        fields = '__all__'
        read_only_fields = ['id', 'uuid', 'created_at', 'updated_at', 'created_by', 'updated_by', 'is_deleted', 'timestamp']
