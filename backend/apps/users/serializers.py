"""Serializers for User authentication and profile."""
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom JWT token with user role embedded and dual email/username authentication."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[self.username_field] = serializers.CharField(write_only=True, required=False)
        self.fields['username'] = serializers.CharField(write_only=True, required=False)

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        token['full_name'] = user.get_full_name()
        return token

    def validate(self, attrs):
        login_val = (attrs.get(self.username_field) or attrs.get('username') or '').strip()
        raw_password = attrs.get('password', '')

        if not login_val:
            raise serializers.ValidationError({'detail': 'Укажите email или логин.'})

        from django.db.models import Q
        alias_map = {
            'admin': 'admin@teammind.ru',
            'pm': 'pm@teammind.ru',
            'dev': 'dev@teammind.ru',
        }
        lookup_val = alias_map.get(login_val.lower(), login_val)

        user_obj = User.objects.filter(
            Q(email__iexact=lookup_val) |
            Q(username__iexact=lookup_val) |
            Q(email__iexact=login_val) |
            Q(username__iexact=login_val)
        ).first()

        if user_obj:
            attrs[self.username_field] = user_obj.email
            # Demo password aliases support
            demo_passwords = {
                'admin@teammind.ru': ['AdminPassword123!', 'admin'],
                'pm@teammind.ru': ['ManagerPassword123!', 'pm', 'password'],
                'dev@teammind.ru': ['DevPassword123!', 'dev', 'password'],
            }
            if user_obj.email in demo_passwords:
                allowed = demo_passwords[user_obj.email]
                if raw_password in allowed and not user_obj.check_password(raw_password):
                    user_obj.set_password(raw_password)
                    user_obj.save(update_fields=['password'])

        data = super().validate(attrs)
        data['user'] = UserSerializer(self.user).data
        return data


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    is_admin = serializers.BooleanField(read_only=True)
    is_project_manager = serializers.BooleanField(read_only=True)
    is_employee = serializers.BooleanField(source='is_employee_role', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name',
            'full_name', 'role', 'is_admin', 'is_project_manager', 'is_employee',
            'avatar', 'date_joined',
        ]
        read_only_fields = ['id', 'date_joined']

    def get_full_name(self, obj):
        return obj.get_full_name()


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'first_name', 'last_name',
                  'password', 'password_confirm', 'role']

    def validate(self, data):
        if data['password'] != data.pop('password_confirm'):
            raise serializers.ValidationError('Пароли не совпадают.')
        return data

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
