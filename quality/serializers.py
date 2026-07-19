from rest_framework import serializers
from .models import QCControl, QCRun, NonConformance

class QCControlSerializer(serializers.ModelSerializer):
    class Meta:
        model = QCControl
        fields = '__all__'
        read_only_fields = ['id', 'uuid', 'created_at', 'updated_at', 'created_by', 'updated_by', 'is_deleted']

class QCRunSerializer(serializers.ModelSerializer):
    control_name = serializers.CharField(source='control.name', read_only=True)

    class Meta:
        model = QCRun
        fields = '__all__'
        read_only_fields = ['id', 'uuid', 'created_at', 'updated_at', 'created_by', 'updated_by', 'is_deleted']

class NonConformanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NonConformance
        fields = '__all__'
        read_only_fields = ['id', 'uuid', 'created_at', 'updated_at', 'created_by', 'updated_by', 'is_deleted']
