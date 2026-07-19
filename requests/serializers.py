from rest_framework import serializers
from .models import TestRequest, RequestedTest
from test_catalogue.serializers import TestSerializer
from encounters.serializers import EncounterSerializer

class RequestedTestSerializer(serializers.ModelSerializer):
    test_detail = TestSerializer(source='test', read_only=True)

    class Meta:
        model = RequestedTest
        fields = '__all__'
        read_only_fields = ['id', 'uuid', 'created_at', 'updated_at', 'created_by', 'updated_by', 'is_deleted', 'price_at_request']

class TestRequestSerializer(serializers.ModelSerializer):
    requested_tests = RequestedTestSerializer(many=True, read_only=True)
    encounter_detail = EncounterSerializer(source='encounter', read_only=True)
    test_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )

    class Meta:
        model = TestRequest
        fields = '__all__'
        read_only_fields = ['id', 'uuid', 'created_at', 'updated_at', 'created_by', 'updated_by', 'is_deleted', 'request_number', 'payment_status']

    def create(self, validated_data):
        test_ids = validated_data.pop('test_ids', [])
        
        # Ensure we set created_by/updated_by if user is authenticated
        request_obj = self.context.get('request')
        user = request_obj.user if request_obj else None
        
        if user and not user.is_anonymous:
            validated_data['created_by'] = user
            validated_data['updated_by'] = user
            
        test_request = TestRequest.objects.create(**validated_data)
        
        from test_catalogue.models import Test
        from billing.models import Invoice
        
        for t_id in test_ids:
            try:
                test_obj = Test.objects.get(id=t_id)
                RequestedTest.objects.create(
                    request=test_request,
                    test=test_obj,
                    price_at_request=test_obj.price,
                    created_by=user,
                    updated_by=user
                )
            except Test.DoesNotExist:
                pass
        
        # Create the Invoice automatically
        Invoice.objects.create(
            request=test_request,
            patient=test_request.encounter.patient,
            created_by=user,
            updated_by=user
        )
        
        return test_request
