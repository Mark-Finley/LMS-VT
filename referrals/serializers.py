from rest_framework import serializers
from .models import ReferralPartner, Referral
from requests.serializers import RequestedTestSerializer

class ReferralPartnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReferralPartner
        fields = '__all__'
        read_only_fields = ['id', 'uuid', 'created_at', 'updated_at', 'created_by', 'updated_by', 'is_deleted']

class ReferralSerializer(serializers.ModelSerializer):
    partner_name = serializers.CharField(source='partner.name', read_only=True)
    requested_test_detail = RequestedTestSerializer(source='requested_test', read_only=True)

    class Meta:
        model = Referral
        fields = '__all__'
        read_only_fields = ['id', 'uuid', 'created_at', 'updated_at', 'created_by', 'updated_by', 'is_deleted']
