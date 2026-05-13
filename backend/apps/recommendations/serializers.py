from rest_framework import serializers
from .models import SavedProduct, SavedRemedy, SkincareRoutine, RoutineLog
from apps.products.serializers import ProductListSerializer, NaturalRemedySerializer


class SavedProductSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = SavedProduct
        fields = ['id', 'product', 'product_id', 'notes', 'created_at']
        read_only_fields = ['id', 'created_at']


class SavedRemedySerializer(serializers.ModelSerializer):
    remedy = NaturalRemedySerializer(read_only=True)
    remedy_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = SavedRemedy
        fields = ['id', 'remedy', 'remedy_id', 'notes', 'created_at']
        read_only_fields = ['id', 'created_at']


class SkincareRoutineSerializer(serializers.ModelSerializer):
    class Meta:
        model = SkincareRoutine
        fields = [
            'id', 'name', 'routine_type', 'description', 'steps',
            'frequency', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class RoutineLogSerializer(serializers.ModelSerializer):
    routine_name = serializers.CharField(source='routine.name', read_only=True)
    
    class Meta:
        model = RoutineLog
        fields = [
            'id', 'routine', 'routine_name', 'routine_type',
            'completed_steps', 'notes', 'completed_at'
        ]
        read_only_fields = ['id', 'completed_at']
