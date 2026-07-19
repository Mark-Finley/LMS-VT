from rest_framework import serializers
from .models import Encounter
from patients.serializers import PatientSerializer

class EncounterSerializer(serializers.ModelSerializer):
    patient_detail = PatientSerializer(source='patient', read_only=True)
    doctor_name = serializers.CharField(source='doctor.get_full_name', read_only=True)

    class Meta:
        model = Encounter
        fields = '__all__'
        read_only_fields = ['id', 'uuid', 'created_at', 'updated_at', 'created_by', 'updated_by', 'is_deleted']
