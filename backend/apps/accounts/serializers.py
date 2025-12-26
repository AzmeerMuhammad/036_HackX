from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, UserProfile


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'password_confirm', 'email', 'display_name')
        extra_kwargs = {
            'email': {'required': False},
            'display_name': {'required': False},
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
        
        user = User.objects.create_user(
            username=validated_data['username'],
            password=password,
            email=email or '',
            display_name=display_name or validated_data['username'],
            is_anonymous_mode=True
        )
        UserProfile.objects.create(user=user)
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'display_name', 'is_anonymous_mode', 'created_at')
        read_only_fields = ('id', 'created_at')

