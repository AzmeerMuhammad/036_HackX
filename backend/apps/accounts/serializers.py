from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'password_confirm', 'email', 'display_name', 'is_professional', 'professional_type')
        extra_kwargs = {
            'email': {'required': False},
            'display_name': {'required': False},
            'is_professional': {'required': False},
            'professional_type': {'required': False},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Passwords don't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        display_name = validated_data.pop('display_name', None)
        email = validated_data.pop('email', None)
        is_professional = validated_data.pop('is_professional', False)
        professional_type = validated_data.pop('professional_type', None)

        user = User.objects.create_user(
            username=validated_data['username'],
            password=password,
            email=email or '',
            display_name=display_name or validated_data['username'],
            is_anonymous_mode=True,
            is_professional=is_professional,
            professional_type=professional_type if is_professional else None
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'display_name', 'is_anonymous_mode', 'is_professional', 'professional_type', 'created_at')
        read_only_fields = ('id', 'created_at')

