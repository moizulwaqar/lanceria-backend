from django.db import transaction
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from .models import *


# Gallery Serializer
class GallerySerializer(serializers.ModelSerializer):
    # user = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field='id', required=True)
    id = serializers.CharField(required=False)
    # service = serializers.SlugRelatedField(queryset=Service.objects.all(), slug_field='id', required=True)
    description = serializers.CharField(required=True)
    file = serializers.URLField(required=True)

    class Meta:
        model = Gallery
        fields = ["id", "description", "file"]


# Service Serializer
class ServiceSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    category = serializers.SlugRelatedField(queryset=Category.objects.all(), slug_field='id', required=True)
    sub_category = serializers.SlugRelatedField(queryset=Category.objects.all(), slug_field='id', required=False)
    title = serializers.CharField(required=True)
    description = serializers.CharField(required=True)
    requirement = serializers.ListField(child=serializers.CharField(required=True), allow_empty=False)
    delivery_day = serializers.IntegerField(required=True)
    revision = serializers.IntegerField(required=False)
    fast_delivery = serializers.IntegerField(required=False)
    additional_revision = serializers.IntegerField(required=False)
    gallery = serializers.ListField(child=serializers.URLField(required=True), allow_empty=False)
    # service_in_gallery = GallerySerializer(many=True, required=True)
    file = serializers.URLField(required=True)
    amount = serializers.IntegerField(required=True)

    class Meta:
        model = Service
        fields = ["id", "category", "sub_category", "title", "description", "requirement", "delivery_day",
                  "revision", "fast_delivery", "additional_revision", "gallery", "file", "amount"]

    # Validate Gallery objects not grater than 5 objects
    def validate(self, attrs):
        gallery = attrs.get("gallery")
        if len(gallery) > 5:
            raise serializers.ValidationError(
                {'Files': _("Limit Exceeded, Max Limit is 5!")})
        return attrs

    # def create(self, validated_data):
    #     gallerys_data = validated_data.pop('service_in_gallery')
    #     if not gallerys_data:
    #         message = {"service_in_gallery": ["This field is required."]}
    #         raise serializers.ValidationError({"statusCode": 400, "error": True, "data": "",
    #                                            "errors": message})
    #     service = Service.objects.create(**validated_data)
    #     for gallery_data in gallerys_data:
    #         Gallery.objects.create(service=service, user=service.user, **gallery_data)
    #     return service


# Service Edit/Update Serializer
class UpdateServiceSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    category = serializers.SlugRelatedField(queryset=Category.objects.all(), slug_field='id', required=True)
    sub_category = serializers.SlugRelatedField(queryset=Category.objects.all(), slug_field='id', required=False)
    title = serializers.CharField(required=True)
    description = serializers.CharField(required=True)
    requirement = serializers.ListField(child=serializers.CharField(required=True), allow_empty=False)
    delivery_day = serializers.IntegerField(required=True)
    revision = serializers.IntegerField(required=False)
    fast_delivery = serializers.IntegerField(required=False)
    additional_revision = serializers.IntegerField(required=False)
    # service_in_gallery = GallerySerializer(many=True, required=True)
    gallery = serializers.ListField(child=serializers.URLField(required=True), allow_empty=False)

    class Meta:
        model = Service
        fields = ["id", "category", "sub_category", "title", "description", "requirement", "delivery_day",
                  "revision", "fast_delivery", "additional_revision", "gallery"]

    # Validate Gallery objects not grater than 5 objects
    def validate(self, attrs):
        if not self.partial:
            gallery = attrs.get("gallery")
            if len(gallery) > 5:
                raise serializers.ValidationError(
                    {'Files': _("Limit Exceeded, Max Limit is 5!")})
            if not gallery:
                message = {"gallery": ["This field is required."]}
                raise serializers.ValidationError(message)
        return attrs

    # def update(self, instance, validated_data):
    #     gallerys_objects = validated_data.pop('service_in_gallery', [])
    #     user_galleys = Gallery.objects.filter(service=instance, user=self.context['user']).count()
    #     with transaction.atomic():
    #         for gallery_obj in gallerys_objects:
    #             gallery_id = gallery_obj.get('id', None)
    #             if gallery_id:
    #                 Gallery.objects.filter(id=gallery_id, service=instance).update(**gallery_obj)
    #             else:
    #                 if user_galleys >= 5:
    #                     errors = {"Files": ["Limit Exceeded, Max Limit is 5!"]}
    #                     raise serializers.ValidationError({"statusCode": 400, "error": True,
    #                                                        "data": "", "message": "Bad Request, Please check request",
    #                                                        "errors": errors})
    #                 Gallery.objects.create(service=instance, user=instance.user, **gallery_obj)
    #                 user_galleys += 1
    #         instance = super(UpdateServiceSerializer, self).update(instance, validated_data)
    #         return instance


class ServiceQuestionSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    service = serializers.SlugRelatedField(queryset=Service.objects.all(), slug_field='id', required=True)
    question = serializers.CharField(required=True)

    class Meta:
        model = ServiceQuestion
        fields = ["id", "service", "question"]


class ServiceAnswerSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    service = serializers.SlugRelatedField(queryset=Service.objects.all(), slug_field='id', required=True)
    answer = serializers.CharField(required=True)

    class Meta:
        model = ServiceAnswer
        fields = ["id", "service", "answer"]
