from django.db import models
from django.contrib.auth.models import AbstractUser
from rest_framework_simplejwt.tokens import RefreshToken
from lanceria_backend.soft_delete import SoftDeleteModel
from django.contrib.postgres.fields import ArrayField

# Create your models here.


class User(AbstractUser, SoftDeleteModel):
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
    USERNAME_FIELD = 'email'
    email = models.EmailField('email address', unique=True)
    cover = models.URLField(null=True, blank=True)
    profile_pic = models.URLField(null=True, blank=True)
    hourly_rate = models.IntegerField(default=0)
    date_of_birth = models.DateField(null=True, blank=True)
    role = models.CharField(max_length=25, choices=ROLE, default="Employer", null=True, blank=True)
    provider = models.CharField(max_length=25, choices=PROVIDER, null=True, blank=True)
    provider_id = models.CharField(max_length=255, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    total_earning = models.DecimalField(max_digits=20, decimal_places=4, default=0.0)
    total_spend = models.DecimalField(max_digits=20, decimal_places=4, default=0.0)
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    newsletter = models.BooleanField(default=False)
    e_uuid = models.CharField(max_length=50, null=True, blank=True)
    f_uuid = models.CharField(max_length=50, null=True, blank=True)

    REQUIRED_FIELDS = []

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }


class UserProfile(SoftDeleteModel):
    ROLE = (
        ("Employer", "Employer"),
        ("Freelancer", "Freelancer"),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_in_user_profile")
    role = models.CharField(max_length=25, choices=ROLE, default="Employer", null=True, blank=True)
    skill = ArrayField(models.CharField(max_length=1000), blank=True, null=True)
    title = models.CharField(max_length=50, null=True, blank=True)
    description = models.CharField(max_length=5000, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
