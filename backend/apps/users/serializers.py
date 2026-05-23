from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    
    password = serializers.CharField(write_only=True, min_length=8, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = [
            'email', 'name', 'password', 'password_confirm',
            'skin_type', 'sensitivity', 'concerns', 'allergies', 'age_group'
        ]
        extra_kwargs = {
            'skin_type': {'required': False},
            'sensitivity': {'required': False},
            'concerns': {'required': False},
            'allergies': {'required': False},
            'age_group': {'required': False},
        }
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({'password_confirm': 'Passwords do not match.'})
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirm', None)
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login."""
    
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user profile."""
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'name', 'phone', 'avatar',
            'skin_type', 'sensitivity', 'concerns', 'allergies', 'age_group', 'climate',
            'notifications_enabled', 'email_updates',
            'is_verified', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'email', 'is_verified', 'created_at', 'updated_at']


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile."""
    
    class Meta:
        model = User
        fields = [
            'name', 'phone', 'avatar',
            'skin_type', 'sensitivity', 'concerns', 'allergies', 'age_group', 'climate',
            'notifications_enabled', 'email_updates'
        ]


class SkinProfileSerializer(serializers.ModelSerializer):
    """Serializer for updating skin profile only."""
    
    class Meta:
        model = User
        fields = ['skin_type', 'sensitivity', 'concerns', 'allergies', 'age_group', 'climate']


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for password change."""
    
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True, min_length=8)
    
    def validate(self, data):
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError({'new_password_confirm': 'Passwords do not match.'})
        return data
