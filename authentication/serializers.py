from datetime import datetime

import django.contrib.auth.password_validation as validators
from django.contrib import auth
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.validators import UniqueValidator

from service.serializers import ServiceSerializer
from user_profile.serializers import LanguageSerializer, LinkedAccountSerializer, UserExperienceSerializer, \
    UserEducationSerializer, UserSkillSerializer
from .models import User

PROVIDER = (
    ("Google", "Google"),
    ("Facebook", "Facebook"),
    ("Apple", "Apple"),
    ("Email", "Email"),
)
ROLE = (
    ("Employer", "Employer"),
    ("Freelancer", "Freelancer"),
)


class SignUpCheckEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate(self, attrs):
        email = attrs["email"]
        if User.objects.filter(email=email.lower()).exists():
            raise serializers.ValidationError({'email': _("User with this email already exist!")})
        return attrs


class EmailSignUpValidationSerializer(serializers.ModelSerializer):
    provider = serializers.ChoiceField(choices=PROVIDER, required=True)
    # role = serializers.ChoiceField(choices=ROLE, required=True)
    password = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    confirm_password = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    username = serializers.CharField(required=True, validators=[
        UniqueValidator(
            queryset=User.objects.all(),
            message="Sorry, user already exist with this username, try with different username.",
        )])
    email = serializers.EmailField(required=True, validators=[
        UniqueValidator(
            queryset=User.objects.all(),
            message="Sorry, user already exist with this email, try with different email.",
        )])

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "password",
                  "confirm_password", "provider", "role"]

    @staticmethod
    def validate_password(data):
        validators.validate_password(password=data, user=User)
        return data

    def validate(self, attrs):
        password = attrs.get("password")
        confirm_password = attrs.get("confirm_password")
        if password != confirm_password:
            raise serializers.ValidationError(
                {'password': _("Your Password not matched!")})

        if User.objects.filter(email=attrs["email"].lower()).exists():
            raise serializers.ValidationError({'email': _
            ("Sorry, user already exist with this email, try with different email.")})
        return attrs


class EmailSignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username', 'email', 'cover', 'profile_pic',
                  'hourly_rate', 'date_of_birth', 'newsletter', 'total_earning', 'total_spend',
                  'role', 'provider', 'f_uuid', 'e_uuid', 'email_verified']


class LoginCheckEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate(self, attrs):
        email = attrs["email"]
        if not User.objects.filter(email=email.lower()).exists():
            raise serializers.ValidationError({'email': _("User with this email not exist!")})
        return attrs


class EmailLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255, required=True)
    password = serializers.CharField(
        max_length=68, write_only=True)
    username = serializers.CharField(
        max_length=255, required=False)

    # tokens = serializers.SerializerMethodField()

    # @staticmethod
    # def get_tokens(obj):
    #     user = User.objects.get(email=obj['email'])
    #
    #     return {
    #         'refresh': user.tokens()['refresh'],
    #         'access': user.tokens()['access']
    #     }

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username', 'email', 'cover', 'profile_pic',
                  'hourly_rate', 'date_of_birth', 'newsletter', 'total_earning', 'total_spend',
                  'password', 'role', 'provider', 'f_uuid', 'e_uuid', 'email_verified']

    def validate(self, attrs):
        email = attrs.get('email', '')
        password = attrs.get('password', '')
        user = auth.authenticate(email=email.lower(), password=password)

        if not user:
            raise AuthenticationFailed('Invalid credentials, try again')
        if not user.is_active:
            raise AuthenticationFailed('Account disabled, contact admin')
        # if not user.is_verified:
        #     raise AuthenticationFailed('Email is not verified')
        user.last_login = datetime.now()
        user.save()
        data = {
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'username': user.username,
            'email': user.email,
            'cover': user.cover,
            'profile_pic': user.profile_pic,
            'hourly_rate': user.hourly_rate,
            'date_of_birth': user.date_of_birth,
            'newsletter': user.newsletter,
            'total_earning': user.total_earning,
            'total_spend': user.total_spend,
            'role': user.role,
            'tokens': user.tokens,
            'provider': user.provider,
            'email_verified': user.email_verified,
            'f_uuid': user.f_uuid,
            'e_uuid': user.e_uuid
        }
        return data
        # return super().validate(attrs)


class UserNameEmailSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255, required=True)
    email = serializers.EmailField(max_length=255, required=True)

    class Meta:
        model = User
        fields = ["username", "email"]

    def validate_email(self, value):
        lower_email = value.lower()
        if User.objects.filter(email__iexact=lower_email).exists():
            raise serializers.ValidationError("User already exist with this email!")
        return lower_email

    def validate(self, attrs):
        username = attrs.get("username")
        if User.objects.filter(username__iexact=username).exists():
            raise serializers.ValidationError(
                {'username': _("User already exist with this username")})
            # raise serializers.ValidationError("User already exist with this username!")
        return attrs


class SocialAuthSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=255, required=True)
    last_name = serializers.CharField(max_length=255, required=True)
    email = serializers.EmailField(max_length=255, required=False)
    provider = serializers.ChoiceField(choices=PROVIDER, required=True)
    role = serializers.CharField(read_only=True)
    provider_id = serializers.CharField(max_length=255, required=True)
    username = serializers.CharField(max_length=255, required=False)
    id = serializers.CharField(read_only=True)

    # email_provide = serializers.BooleanField(required=True)

    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "username", "email", "provider", "role", "provider_id"]

    def validate(self, attrs):
        if User.objects.filter(provider_id=attrs.get("provider_id"), provider=attrs.get("provider")).exists():
            return attrs
        else:
            serializer = UserNameEmailSerializer(data=attrs)
            serializer.is_valid(raise_exception=True)
            user = User(**attrs)
            user.save()
        return attrs


class GenerateUserName(serializers.Serializer):
    first_name = serializers.CharField(max_length=255, required=True)
    last_name = serializers.CharField(max_length=255, required=True)


class RoleChangeSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=ROLE, required=True)


class ForgotPasswordSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ("email",)

    @staticmethod
    def validate_email(value):
        lower_email = value.lower()
        if not User.objects.filter(email__iexact=lower_email).exists():
            raise serializers.ValidationError("Email does not exist!")
        return lower_email


class ResetPasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(required=True, write_only=True)
    confirm_password = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = User
        fields = ("password", "confirm_password")

    @staticmethod
    def validate_password(data):
        validators.validate_password(password=data, user=User)
        return data

    def validate(self, attrs):
        new_password = attrs.get("password")
        confirm_password = attrs.get("confirm_password")
        if new_password != confirm_password:
            raise serializers.ValidationError(
                {'password': _("Your Password not matched!")})
        return attrs


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=True)


class FreelancerViewSerializer(serializers.ModelSerializer):
    joined = serializers.DateTimeField(source="date_joined", read_only=True, format="%B %d,%Y")
    experience = UserExperienceSerializer(many=True, read_only=True, source="user_in_experience")
    education = UserEducationSerializer(many=True, read_only=True, source="user_in_education")
    language = LanguageSerializer(many=True, read_only=True, source="user_in_language")
    linked_account = LinkedAccountSerializer(many=True, read_only=True, source="user_in_linked_account")
    skill = UserSkillSerializer(many=True, read_only=True, source="user_in_user_skill")
    service = ServiceSerializer(many=True, read_only=True, source="user_in_service")

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "cover", "role", "profile_pic",
                  "hourly_rate", "joined", "language", "linked_account", "service", "experience",
                  "education", "skill", "email_verified", 'f_uuid', 'e_uuid']


class EmployerViewSerializer(serializers.ModelSerializer):
    joined = serializers.DateTimeField(source="date_joined", read_only=True, format="%B %d,%Y")
    language = LanguageSerializer(many=True, read_only=True, source="user_in_language")
    linked_account = LinkedAccountSerializer(many=True, read_only=True, source="user_in_linked_account")

    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email", "cover", "role", "profile_pic", "joined",
                  "language",
                  "linked_account", "email_verified", 'f_uuid', 'e_uuid']
