from rest_framework import serializers
from .models import Professional, ProfessionalSOPDoc, EscalationTicket
from apps.accounts.serializers import UserSerializer


class ProfessionalSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    is_profile_complete = serializers.SerializerMethodField()
    profile_completion_percentage = serializers.SerializerMethodField()
    missing_fields = serializers.SerializerMethodField()
    
    class Meta:
        model = Professional
        fields = ('id', 'user', 'specialization', 'availability', 'verified', 'city', 
                  'created_at', 'is_profile_complete', 'profile_completion_percentage', 'missing_fields')
        read_only_fields = ('id', 'created_at', 'is_profile_complete', 'profile_completion_percentage', 'missing_fields')
    
    def get_is_profile_complete(self, obj):
        return obj.is_profile_complete()
    
    def get_profile_completion_percentage(self, obj):
        return obj.get_profile_completion_percentage()
    
    def get_missing_fields(self, obj):
        return obj.get_missing_fields()


class ProfessionalApplySerializer(serializers.ModelSerializer):
    specialization = serializers.CharField(required=False, allow_blank=True)
    city = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        model = Professional
        fields = ('specialization', 'availability', 'city')

    def validate(self, attrs):
        """Validate that required fields are provided when updating profile."""
        # Only validate if we're updating an existing instance (profile completion)
        if self.instance is not None:
            # When updating, check if fields being updated would make profile incomplete
            specialization = attrs.get('specialization', self.instance.specialization)
            city = attrs.get('city', self.instance.city)
            
            # If both are being set, they must not be empty
            if 'specialization' in attrs and not specialization or not specialization.strip():
                raise serializers.ValidationError({"specialization": "Specialization cannot be empty."})
            if 'city' in attrs and not city or not city.strip():
                raise serializers.ValidationError({"city": "City cannot be empty."})
        
        return attrs

    def create(self, validated_data):
        user = self.context['request'].user
        professional, created = Professional.objects.get_or_create(
            user=user,
            defaults={
                'specialization': validated_data['specialization'],
                'availability': validated_data.get('availability', ''),
                'city': validated_data.get('city', ''),
                'verified': False  # Will be auto-verified in save() if complete
            }
        )
        if not created:
            for key, value in validated_data.items():
                setattr(professional, key, value)
            professional.save()  # This will auto-verify if profile is complete
        return professional


class ProfessionalSOPDocSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfessionalSOPDoc
        fields = ('id', 'title', 'category', 'content', 'active', 'created_at')
        read_only_fields = ('id', 'created_at')


class EscalationTicketSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    assigned_professional = ProfessionalSerializer(read_only=True)
    
    class Meta:
        model = EscalationTicket
        fields = ('id', 'session', 'user', 'assigned_professional', 'reason', 'status', 
                  'verdict', 'professional_notes', 'created_at', 'reviewed_at')
        read_only_fields = ('id', 'created_at', 'reviewed_at')


class EscalationVerdictSerializer(serializers.Serializer):
    verdict = serializers.ChoiceField(choices=EscalationTicket.VERDICT_CHOICES)
    professional_notes = serializers.CharField(required=False, allow_blank=True)

