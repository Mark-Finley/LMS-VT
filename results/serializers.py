from rest_framework import serializers
from .models import Result, ParameterResultValue
from requests.serializers import RequestedTestSerializer

class ParameterResultValueSerializer(serializers.ModelSerializer):
    parameter_name = serializers.CharField(source='parameter.name', read_only=True)
    parameter_range = serializers.CharField(source='parameter.normal_range', read_only=True)
    parameter_units = serializers.CharField(source='parameter.units', read_only=True)

    class Meta:
        model = ParameterResultValue
        fields = '__all__'
        read_only_fields = ['id', 'uuid', 'created_at', 'updated_at', 'created_by', 'updated_by', 'is_deleted']

class ResultSerializer(serializers.ModelSerializer):
    requested_test_detail = RequestedTestSerializer(source='requested_test', read_only=True)
    recorded_by_name = serializers.CharField(source='recorded_by.username', read_only=True)
    reviewed_by_name = serializers.CharField(source='reviewed_by.username', read_only=True)
    verified_by_name = serializers.CharField(source='verified_by.username', read_only=True)
    parameter_values = ParameterResultValueSerializer(many=True, required=False)

    class Meta:
        model = Result
        fields = '__all__'
        read_only_fields = ['id', 'uuid', 'created_at', 'updated_at', 'created_by', 'updated_by', 'is_deleted', 'recorded_by', 'recorded_at', 'reviewed_by', 'reviewed_at', 'verified_by', 'verified_at', 'electronic_signature']

    def create(self, validated_data):
        parameter_values_data = validated_data.pop('parameter_values', [])
        result = Result.objects.create(**validated_data)
        for pv_data in parameter_values_data:
            ParameterResultValue.objects.create(result=result, **pv_data)
        return result

    def update(self, instance, validated_data):
        parameter_values_data = validated_data.pop('parameter_values', [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if parameter_values_data:
            instance.parameter_values.all().delete()
            for pv_data in parameter_values_data:
                ParameterResultValue.objects.create(result=instance, **pv_data)
        return instance
