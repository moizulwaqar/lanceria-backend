from django.db import models
from datetime import timezone, datetime
from authentication.models import User
from lanceria_backend.soft_delete import SoftDeleteModel
from django.contrib.postgres.fields import ArrayField
# Create your models here.


class Skill(SoftDeleteModel):
    name = models.CharField(max_length=255)


class Education(SoftDeleteModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_in_education")
    country = models.CharField(max_length=255, null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    institute = models.CharField(max_length=255, null=True, blank=True)
    study_area = models.CharField(max_length=255, null=True, blank=True)
    start = models.DateField(null=True, blank=True)
    end = models.DateField(null=True, blank=True)
    present = models.BooleanField(default=False)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Experience(SoftDeleteModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_in_experience")
    country = models.CharField(max_length=255, null=True, blank=True)
    company_name = models.CharField(max_length=255, null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    start = models.DateField(null=True, blank=True)
    end = models.DateField(null=True, blank=True)
    present = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Portfolio(SoftDeleteModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_in_portfolio")
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    image = models.FileField(upload_to="portfolio_image/", null=True, blank=True)
    video = models.FileField(upload_to="portfolio_video/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Language(SoftDeleteModel):
    LEVEL = (
        ("Basic", "Basic"),
        ("Native", "Native"),
        ("Fluent", "Fluent"),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_in_language")
    name = models.CharField(max_length=30, null=True, blank=True)
    level = models.CharField(max_length=25, choices=LEVEL, default="Basic")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class LinkedAccount(SoftDeleteModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_in_linked_account")
    url = models.URLField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class UserSkill(SoftDeleteModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_in_user_skill")
    # skill = models.ForeignKey(Skill, on_delete=models.SET_NULL, null=True, blank=True,
    #                           related_name="skill_in_user_skill")
    skills = ArrayField(models.CharField(max_length=1000), blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Certification(SoftDeleteModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_in_certification")
    name = models.CharField(max_length=255, null=True, blank=True)
    provider_name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    start = models.DateField(null=True, blank=True)
    end = models.DateField(null=True, blank=True)
    certification_id = models.CharField(max_length=255, null=True, blank=True)
    url = models.URLField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
