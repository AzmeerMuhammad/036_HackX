from rest_framework import serializers
from .models import Professional, ProfessionalSOPDoc, EscalationTicket
from apps.accounts.serializers import UserSerializer


class ProfessionalSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Professional
        fields = ('id', 'user', 'specialization', 'availability', 'verified', 'city', 'created_at')
        read_only_fields = ('id', 'created_at')


class ProfessionalApplySerializer(serializers.ModelSerializer):
    class Meta:
        model = Professional
        fields = ('specialization', 'availability', 'city')

    def create(self, validated_data):
        user = self.context['request'].user
        professional, created = Professional.objects.get_or_create(
            user=user,
            defaults={
                'specialization': validated_data['specialization'],
                'availability': validated_data.get('availability', ''),
                'city': validated_data.get('city', ''),
                'verified': False
            }
        )
        if not created:
            for key, value in validated_data.items():
                setattr(professional, key, value)
            professional.save()
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

