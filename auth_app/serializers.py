from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'role', 'email_verified']
        read_only_fields = ['id', 'email_verified']


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    remember = serializers.BooleanField(required=False, default=False)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            # Try authenticating with email
            user = authenticate(username=email, password=password)
            if not user:
                raise serializers.ValidationError('Invalid email or password.')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled.')
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Must include email and password.')

        return attrs


class BusinessSerializer(serializers.Serializer):
    business_name = serializers.CharField(max_length=120, required=True)
    website = serializers.URLField(required=False, allow_blank=True)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)
    business = BusinessSerializer(required=False)
    accept_tos = serializers.BooleanField(write_only=True)
    marketing_opt_in = serializers.BooleanField(default=False)

    class Meta:
        model = User
        fields = [
            'role', 'first_name', 'last_name', 'email', 'password', 
            'confirm_password', 'business', 'accept_tos', 'marketing_opt_in'
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords don't match.")
        
        if not attrs.get('accept_tos'):
            raise serializers.ValidationError("You must accept the Terms of Service.")
        
        if attrs.get('role') == 'business' and not attrs.get('business', {}).get('business_name'):
            raise serializers.ValidationError("Business name is required for business accounts.")
        
        return attrs

    def validate_password(self, value):
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value

    def create(self, validated_data):
        business_data = validated_data.pop('business', {})
        validated_data.pop('confirm_password')
        validated_data.pop('accept_tos')
        
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        
        # Set business fields if role is business
        if user.role == 'business' and business_data:
            user.business_name = business_data.get('business_name')
            user.website = business_data.get('website')
            user.phone = business_data.get('phone')
            user.save()
        
        return user


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField()
    password = serializers.CharField(min_length=8)

    def validate_password(self, value):
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value
