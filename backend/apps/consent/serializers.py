from rest_framework import serializers
from .models import ConsentGrant
from apps.professionals.serializers import ProfessionalSerializer


class ConsentGrantSerializer(serializers.ModelSerializer):
    professional = ProfessionalSerializer(read_only=True)
    
    class Meta:
        model = ConsentGrant
        fields = ('id', 'professional', 'active', 'created_at')
        read_only_fields = ('id', 'created_at')


class ConsentGrantCreateSerializer(serializers.Serializer):
    professional_id = serializers.IntegerField()

