from django.core.paginator import Paginator
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from datetime import date
from authentication.models import User, UserProfile
from .models import Skill, Education, Experience, Portfolio, LinkedAccount, Language, Certification, UserSkill
# from authentication.serializers import LinkedAccountSerializer
from job.serializers import UserJobListSerializer
from job.models import Job


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = "__all__"


class ListOfSkillSerializer(serializers.ModelSerializer):
    label = serializers.CharField(source="name")
    value = serializers.CharField(source="name")

    class Meta:
        model = Skill
        fields = ["label", "value"]


def profile_image_validator(file):
    max_file_size = 1024 * 1024 * 2  # 2MB
    if file.size > max_file_size:
        raise serializers.ValidationError(_('Max file size is 2MB'))


class UpdateProfileSerializer(serializers.ModelSerializer):
    # id = serializers.CharField(read_only=True)
    skill = serializers.ListField(child=serializers.CharField(required=False, allow_null=True, allow_blank=True),
                                  required=False)
    # title = serializers.CharField(max_length=50, required=False)
    # description = serializers.CharField(max_length=5000, required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = UserProfile
        fields = ["skill", "title", "description", ]

class LinkedAccountSerializer(serializers.ModelSerializer):
    url = serializers.URLField(required=True)
    id = serializers.CharField(read_only=True)

    class Meta:
        model = LinkedAccount
        fields = ["id", "url"]

class UserSkillSerializer(serializers.ModelSerializer):
    # skill = serializers.SlugRelatedField(queryset=Skill.objects.all(), slug_field='id')
    # skill_name = serializers.CharField(source="skill.name", read_only=True)
    skills = serializers.ListField(child=serializers.CharField(required=True))

    class Meta:
        model = UserSkill
        fields = ['id', 'skills']


class FreelancerProfileSerializer(serializers.ModelSerializer):
    # profile_pic = serializers.FileField(validators=[profile_image_validator], required=False)
    profile_pic = serializers.URLField(required=False)
    title = serializers.CharField(max_length=50, required=False)
    description = serializers.CharField(max_length=5000, required=False)
    skill = serializers.ListField(child=serializers.CharField(required=True), required=False)
    # cover = serializers.FileField(validators=[profile_image_validator], required=False)
    cover = serializers.URLField(required=False)
    email = serializers.EmailField(read_only=True)
    username = serializers.CharField(read_only=True)
    joined = serializers.DateTimeField(source="date_joined", read_only=True, format="%B %d,%Y")

    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "profile_pic", "cover", "hourly_rate", "role",
                  "email", "username", "joined", "email_verified", "title", "description", "skill"]


class FreelancerDashboardSerializer(FreelancerProfileSerializer):
    e_uuid = serializers.CharField(read_only=True)
    f_uuid = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = FreelancerProfileSerializer.Meta.fields + ['e_uuid', 'f_uuid', "role"]


class EmployerProfileSerializer(serializers.ModelSerializer):
    profile_pic = serializers.URLField(required=False)
    # profile_pic = serializers.FileField(validators=[profile_image_validator], required=False)
    # cover = serializers.FileField(validators=[profile_image_validator], required=False)
    cover = serializers.URLField(required=False)
    email = serializers.EmailField(read_only=True)
    username = serializers.CharField(read_only=True)
    joined = serializers.DateTimeField(source="date_joined", read_only=True, format="%B %d,%Y")

    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "profile_pic", "cover",
                  "email", "username", "joined", "email_verified", "role"]


class EmployerDashboardSerializer(EmployerProfileSerializer):
    e_uuid = serializers.CharField(read_only=True)
    f_uuid = serializers.CharField(read_only=True)
    linked_account = LinkedAccountSerializer(many=True, read_only=True, source="user_in_linked_account")
    skills = serializers.SerializerMethodField()
    # jobs = serializers.SerializerMethodField()
    # no_of_jobs = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = EmployerProfileSerializer.Meta.fields + ['e_uuid', 'f_uuid', "role", "linked_account", "skills"]

    def get_skills(self, obj):
        profile = UserProfile.objects.filter(user=obj, role="Employer").first()
        return profile.skill

    # def get_jobs(self, obj):
    #     page_size = 5
    #     job_list = Job.objects.filter(user=obj)
    #     paginator = Paginator(job_list.order_by('-id'), page_size)
    #     page = self.context['request'].query_params.get('page') or 1
    #     if int(page) > (paginator.page_range.stop - 1):
    #         return []
    #     jobs = paginator.page(page)
    #     serializer = UserJobListSerializer(jobs, many=True)
    #     return serializer.data
    #
    # def get_no_of_jobs(self, obj):
    #     jobs = Job.objects.filter(user=obj).count()
    #     return jobs


class UserEducationSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    country = serializers.CharField(required=True)
    institute = serializers.CharField(required=True)
    study_area = serializers.CharField(required=True)
    degree = serializers.CharField(source="title", required=True)
    start = serializers.DateField(required=True)
    end = serializers.DateField(required=False)
    description = serializers.CharField(required=False)

    class Meta:
        model = Education
        fields = ["id", "country", "institute", "degree", "start", "end", "description", "present", "study_area"]

    def validate(self, attrs):
        if "start" in attrs:
            if attrs["start"] > date.today():
                raise serializers.ValidationError(
                    {'start_date': _("Please make sure your start date should be equal"
                                     "current date or less than current date!")})
        return attrs


class UserExperienceSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    country = serializers.CharField(required=False)
    title = serializers.CharField(required=True)
    company_name = serializers.CharField(required=True)
    start = serializers.DateField(required=True)
    end = serializers.DateField(required=False)
    description = serializers.CharField(required=True)

    class Meta:
        model = Experience
        fields = ["id", "country", "title", "company_name", "start", "end", "present", "description"]

    def validate(self, attrs):
        if "start" in attrs:
            if attrs["start"] > date.today():
                raise serializers.ValidationError(
                    {'start_date': _("Please make sure your start date should be equal"
                                     "current date or less than current date!")})
        if "end" in attrs:
            if attrs["end"] > date.today():
                raise serializers.ValidationError(
                    {'end_date': _(
                        "Please make sure your end date should be equal current date or less than current date!")})
        return attrs


def video_validator(file):
    max_file_size = 1024 * 1024 * 100  # 2MB
    if file.size > max_file_size:
        raise serializers.ValidationError(_('Max file size is 100MB'))


def image_validator(file):
    max_file_size = 1024 * 1024 * 7  # 2MB
    if file.size > max_file_size:
        raise serializers.ValidationError(_('Max file size is 7MB'))


class UserPortfolioSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    title = serializers.CharField(required=True)
    description = serializers.CharField(required=True)
    image = serializers.FileField(validators=[image_validator], required=False)
    video = serializers.FileField(validators=[video_validator], required=False)

    class Meta:
        model = Portfolio
        fields = ["id", "title", "description", "image", "video"]





class LanguageSerializer(serializers.ModelSerializer):
    LEVEL = (
        ("Basic", "Basic"),
        ("Native", "Native"),
        ("Fluent", "Fluent"),
    )
    level = serializers.ChoiceField(choices=LEVEL, required=True)
    name = serializers.CharField(required=True)
    id = serializers.CharField(read_only=True)

    class Meta:
        model = Language
        fields = ["id", "name", "level"]

    def validate(self, attrs):
        name = attrs["name"]
        if Language.objects.filter(name=name, user=self.context['user']).exists():
            raise serializers.ValidationError(
                {'name': _("Language Already exist")})
        if Language.objects.filter(user=self.context['user']).count() >= 5:
            message = {"language": ["Limit Exceeded, Max Limit is 5!"]}
            raise serializers.ValidationError(message)
        return attrs


class UpdateLanguageSerializer(serializers.ModelSerializer):
    LEVEL = (
        ("Basic", "Basic"),
        ("Native", "Native"),
        ("Fluent", "Fluent"),
    )
    level = serializers.ChoiceField(choices=LEVEL, required=True)
    name = serializers.CharField(required=True)
    id = serializers.CharField(read_only=True)

    class Meta:
        model = Language
        fields = ["id", "name", "level"]

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.level = validated_data.get('level', instance.level)
        if Language.objects.filter(name=validated_data.get('name'), user=self.context['user']).exclude(id=instance.id).exists():
            errors = {"name": ["Language Already exist"]}
            raise serializers.ValidationError({"statusCode": 400, "error": True,
                                               "data": "", "message": "Bad Request, Please check request",
                                               "errors": errors})
        instance.save()
        return instance


class CertificationSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    name = serializers.CharField(required=True)
    provider_name = serializers.CharField(required=True)
    description = serializers.CharField(required=True)
    certification_id = serializers.CharField(required=False)
    url = serializers.URLField(required=False)
    start = serializers.DateField(required=True)
    end = serializers.DateField(required=True)

    class Meta:
        model = Certification
        fields = ["id", "name", "provider_name", "description", "certification_id", "url", "start", "end"]


class ProfileListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "username", "email", "role"]


class ViewFreelancerProfile(serializers.ModelSerializer):
    certification = CertificationSerializer(many=True, read_only=True, source="user_in_certification")
    portfolio = UserPortfolioSerializer(many=True, source="user_in_portfolio")
    experience = UserExperienceSerializer(many=True, read_only=True, source="user_in_experience")
    education = UserEducationSerializer(many=True, read_only=True, source="user_in_education")
    language = LanguageSerializer(many=True, read_only=True, source="user_in_language")
    linked_account = LinkedAccountSerializer(many=True, read_only=True, source="user_in_linked_account")
    skill = LinkedAccountSerializer(many=True, read_only=True, source="user_in_user_skill")

    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email", "cover", "profile_pic", "title", "description",
                  "hourly_rate", "date_of_birth", "role", "date_joined", "certification", "portfolio", "experience",
                  "education", "language", "linked_account", "skill", "email_verified"]





class GetFreelancerProfileSerializer(FreelancerProfileSerializer):
    e_uuid = serializers.CharField(read_only=True)
    f_uuid = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = FreelancerProfileSerializer.Meta.fields + ['e_uuid', 'f_uuid']


class GetEmployerProfileSerializer(EmployerProfileSerializer):
    e_uuid = serializers.CharField(read_only=True)
    f_uuid = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = EmployerProfileSerializer.Meta.fields + ['e_uuid', 'f_uuid']