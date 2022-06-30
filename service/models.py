from django.contrib.postgres.fields import ArrayField
from django.db import models
from lanceria_backend.soft_delete import SoftDeleteModel
from authentication.models import User
from category_management.models import Category
# Create your models here.


class Service(SoftDeleteModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_in_service")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="category_in_service")
    sub_category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="sub_category_in_service")
    title = models.CharField(max_length=150, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    tag = ArrayField(models.CharField(max_length=1000), blank=True, null=True)
    gallery = ArrayField(models.URLField(null=True, blank=True), blank=True, null=True)
    delivery_day = models.IntegerField(default=1)
    revision = models.IntegerField(default=0)
    fast_delivery = models.IntegerField(default=0)
    amount = models.CharField(max_length=50, null=True, blank=True)
    additional_revision = models.IntegerField(default=0)
    requirement = ArrayField(models.CharField(max_length=1000), blank=True, null=True)
    file = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Gallery(SoftDeleteModel):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="service_in_gallery")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_in_gallery")
    description = models.TextField(null=True, blank=True)
    file = models.URLField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ServiceQuestion(SoftDeleteModel):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="service_in_service_question")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_in_service_question")
    question = models.CharField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ServiceAnswer(SoftDeleteModel):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="service_in_service_answer")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_in_service_answer")
    answer = models.CharField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
