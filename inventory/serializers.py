from rest_framework import serializers
from .models import Supplier, Reagent, StockTransaction

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'
        read_only_fields = ['id', 'uuid', 'created_at', 'updated_at', 'created_by', 'updated_by', 'is_deleted']

class ReagentSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)

    class Meta:
        model = Reagent
        fields = '__all__'
        read_only_fields = ['id', 'uuid', 'created_at', 'updated_at', 'created_by', 'updated_by', 'is_deleted', 'current_quantity']

class StockTransactionSerializer(serializers.ModelSerializer):
    reagent_name = serializers.CharField(source='reagent.name', read_only=True)

    class Meta:
        model = StockTransaction
        fields = '__all__'
        read_only_fields = ['id', 'uuid', 'created_at', 'updated_at', 'created_by', 'updated_by', 'is_deleted']
