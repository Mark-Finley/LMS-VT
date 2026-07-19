from rest_framework import serializers
from .models import Patient

class PatientSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = Patient
        fields = '__all__'
        read_only_fields = ['id', 'uuid', 'created_at', 'updated_at', 'created_by', 'updated_by', 'is_deleted']
