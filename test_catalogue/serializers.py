from rest_framework import serializers
from .models import Test, TestCategory, TestParameter

class TestCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TestCategory
        fields = '__all__'
        read_only_fields = ['id', 'uuid', 'created_at', 'updated_at', 'created_by', 'updated_by', 'is_deleted']

class TestParameterSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestParameter
        fields = '__all__'
        read_only_fields = ['id', 'uuid', 'created_at', 'updated_at', 'created_by', 'updated_by', 'is_deleted']

class TestSerializer(serializers.ModelSerializer):
    category_detail = TestCategorySerializer(source='category', read_only=True)
    parameters = TestParameterSerializer(many=True, read_only=True)

    class Meta:
        model = Test
        fields = '__all__'
        read_only_fields = ['id', 'uuid', 'created_at', 'updated_at', 'created_by', 'updated_by', 'is_deleted']
