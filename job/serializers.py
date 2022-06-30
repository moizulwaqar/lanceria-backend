from django.db import transaction
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.serializers import raise_errors_on_nested_writes
from rest_framework.utils import model_meta
import timeago
from datetime import datetime, timezone
from .models import Job, JobSkill, JobQuestions
from category_management.models import Category
from user_profile.models import Skill
from bid.models import Bid


class JobSkillSerializer(serializers.ModelSerializer):
    # id = serializers.CharField(read_only=True)
    # job = serializers.SlugRelatedField(queryset=Job.objects.all(), slug_field='id', required=False,
    #                                    source="job_in_job_skill")
    # # skill = serializers.SlugRelatedField(queryset=Skill.objects.all(), slug_field='id', required=True,
    # #                                      source="skill_in_job_skill")
    skills = serializers.ListField(child=serializers.CharField(required=True))

    class Meta:
        model = JobSkill
        # fields = "__all__"
        fields = ["skills"]


class JobQuestionSerializer(serializers.ModelSerializer):
    id = serializers.CharField(required=False)
    job = serializers.SlugRelatedField(queryset=Job.objects.all(), slug_field='id', required=False,
                                       source="job_in_job_skill")
    question = serializers.CharField(required=True, max_length=255)

    class Meta:
        model = JobQuestions
        fields = ["id", "job", "question"]


class JobSerializer(serializers.ModelSerializer):
    LEVEL = (
        ("Rising Talent", "Rising Talent"),
        ("Intermediate", "Intermediate"),
        ("Ultra Pro", "Ultra Pro"),
    )
    ENGLISH_LEVEL = (
        ("Basic", "Basic"),
        ("Native", "Native"),
        ("Fluent", "Fluent"),
    )
    PROJECT_LEVEL = (
        ("One Time", "One Time"),
        ("Ongoing", "Ongoing"),
        ("Complex", "Complex"),
    )
    DURATION = (
        ("0-1 Month", "0-1 Month"),
        ("1-2 Months", "1-2 Months"),
        ("2-4 Months", "2-4 Months"),
        ("4-6 Months", "4-6 Months"),
        ("6 Months to 1 Year", "6 Months to 1 Year"),
        ("1 Year +", "1 Year +"),
    )
    SUCCESS = (
        ("70-80", "70-80"),
        ("80-90", "80-90"),
        ("90+", "90+"),
        ("Any", "Any"),
    )
    BUDGET_TYPE = (
        ("Fixed", "Fixed"),
        ("Per Hour", "Per Hour"),

    )
    id = serializers.CharField(read_only=True)
    title = serializers.CharField(required=True)
    description = serializers.CharField(required=True)
    category = serializers.SlugRelatedField(queryset=Category.objects.all(), slug_field='id', required=True)
    sub_category = serializers.SlugRelatedField(queryset=Category.objects.all(), slug_field='id', required=True)
    level = serializers.ChoiceField(choices=LEVEL, required=True)
    english_level = serializers.ChoiceField(choices=ENGLISH_LEVEL, required=True)
    project_level = serializers.ChoiceField(choices=PROJECT_LEVEL, required=True)
    duration = serializers.ChoiceField(choices=DURATION, required=True)
    location = serializers.ListField(child=serializers.CharField(required=False, max_length=1000))
    success = serializers.ChoiceField(choices=SUCCESS, allow_null=True, allow_blank=True)
    budget_type = serializers.ChoiceField(choices=BUDGET_TYPE, required=True)
    budget = serializers.IntegerField(required=True)
    file = serializers.URLField(required=False, allow_blank=True)
    # skill = JobSkillSerializer(many=True, required=True, write_only=True)
    skills = serializers.ListField(child=serializers.CharField(required=True))
    questions = JobQuestionSerializer(many=True, source="job_in_job_questions", required=False)
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = ["id", "title", "description", "category", "sub_category", "level", "english_level", "project_level",
                  "duration", "location", "success", "budget_type", "budget", "skills", "questions", "file", "created_at"]

    def validate(self, attrs):
        if not self.partial:
            if (len(attrs["title"]) > 50 or len(attrs["title"]) < 20) and (len(attrs["description"]) > 5000 or
                                                                           len(attrs["description"]) < 50):
                raise serializers.ValidationError(
                    {'title': _("Ensure this field has no less than 20 characters and no more than 50 characters!"),
                     'description': _("Ensure this field has no less than 50 characters and no more than 5000 characters!")})

            if len(attrs["title"]) > 50 or len(attrs["title"]) < 20:
                raise serializers.ValidationError(
                    {'title': _("Ensure this field has no less than 20 characters and no more than 50 characters!")})

            if len(attrs["description"]) > 5000 or len(attrs["description"]) < 50:
                raise serializers.ValidationError(
                    {'description': _("Ensure this field has no less than 50 characters and no more than 5000 characters!")})
            # if not attrs.get("job_in_job_questions"):
            #     raise serializers.ValidationError(
            #         {'questions': _(
            #             "This field is required.")})
            if len(attrs.get("job_in_job_questions")) > 5:
                raise serializers.ValidationError({
                    "questions": _("Limit exceeded, Max limit is 5")
                })
            return attrs
        else:
            if "title" in attrs or "description" in attrs:
                if "description" in attrs and "title" in attrs:
                    if (len(attrs["title"]) > 50 or len(attrs["title"]) < 20) and (len(attrs["description"]) > 5000 or
                                                                                   len(attrs["description"]) < 50):
                        raise serializers.ValidationError(
                            {'title': _("Ensure this field has no less than 20 characters and no more than 50 characters!"),
                             'description': _(
                                 "Ensure this field has no less tha`n 50 characters and no more than 5000 characters!")})
                if "title" in attrs:
                    if len(attrs["title"]) > 50 or len(attrs["title"]) < 20:
                        raise serializers.ValidationError(
                            {'title': _(
                                "Ensure this field has no less than 20 characters and no more than 50 characters!")})

                if "description" in attrs:
                    if len(attrs["description"]) > 5000 or len(attrs["description"]) < 50:
                        raise serializers.ValidationError(
                            {'description': _(
                                "Ensure this field has no less than 50 characters and no more than 5000 characters!")})



            return attrs

    # @staticmethod
    # def validate_title(value):
    #     if 50 < len(value) < 20:
    #         raise serializers.ValidationError(
    #             "Ensure this field has no less than 20 characters and no more than 50 characters!")
    #     return value

    def create(self, validated_data):
        # skill_data = validated_data.pop('user_in_job_skill')
        question_data = validated_data.pop('job_in_job_questions')
        with transaction.atomic():
            job = Job.objects.create(**validated_data)
            # for data in skill_data:
            # JobSkill.objects.create(job=job, user=validated_data.get("user"), **skill_data)
            for data in question_data:
                JobQuestions.objects.create(job=job, user=validated_data.get("user"), **data)
            return job

    def update(self, instance, validated_data):
        if "job_in_job_questions" in validated_data:
            question_data = validated_data.pop('job_in_job_questions')
        else:
            question_data = ""
        with transaction.atomic():

            for data in question_data:
                if data.get("id"):
                    JobQuestions.objects.filter(id=data.get("id")).update(**data)
                else:
                    JobQuestions.objects.create(job=instance, user=instance.user, **data)
            instance = super(JobSerializer, self).update(instance, validated_data)
            return instance

    def get_created_at(self, obj):
        now = datetime.now(timezone.utc)
        return timeago.format(obj.created_at, now)


class JobListSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = ["id", "title", "description", "budget_type", "level", "budget", "created_at", "duration"]

    def get_created_at(self, obj):
        now = datetime.now(timezone.utc)
        return timeago.format(obj.created_at, now)


class UserJobListSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField()
    no_of_bids = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = ["id", "title", "description", "budget_type", "level", "budget", "created_at", "duration", "no_of_bids"]

    def get_created_at(self, obj):
        now = datetime.now(timezone.utc)
        return timeago.format(obj.created_at, now)

    def get_no_of_bids(self, obj):
        bids = Bid.objects.filter(job=obj).count()
        return bids


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ["id", "name"]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]