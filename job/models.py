from django.contrib.postgres.fields import ArrayField
from django.db import models
from user_profile.models import Skill
from authentication.models import User
from category_management.models import Category
from lanceria_backend.soft_delete import SoftDeleteModel


# Create your models here.


class Job(SoftDeleteModel):
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
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_in_job")
    # length min 20 and max 50
    title = models.CharField(max_length=50, null=True, blank=True)
    description = models.CharField(max_length=5000, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="category_in_job")
    sub_category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="sub_category_in_job", null=True,
                                     blank=True)
    level = models.CharField(max_length=25, choices=LEVEL, default="Rising Talent")
    english_level = models.CharField(max_length=25, choices=ENGLISH_LEVEL, default="Basic")
    project_level = models.CharField(max_length=25, choices=PROJECT_LEVEL, default="One Time")
    duration = models.CharField(max_length=25, choices=DURATION, default="0-1 Month")
    location = ArrayField(models.CharField(max_length=1000), blank=True, null=True)
    success = models.CharField(max_length=25, choices=SUCCESS, default="Any")
    budget_type = models.CharField(max_length=25, choices=BUDGET_TYPE, default="Fixed")
    skills = ArrayField(models.CharField(max_length=1000), blank=True, null=True)
    budget = models.IntegerField(null=True, blank=True)
    file = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class JobQuestions(SoftDeleteModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_in_job_questions")
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="job_in_job_questions")
    question = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class JobSkill(SoftDeleteModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_in_job_skill")
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="job_in_job_skill")
    # skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name="skill_in_job_skill")
    skills = ArrayField(models.CharField(max_length=1000), blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)