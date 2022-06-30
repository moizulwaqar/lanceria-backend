from django.db import models
from lanceria_backend.soft_delete import SoftDeleteModel
from authentication.models import User
from job.models import Job, JobQuestions
# Create your models here.


class Bid(SoftDeleteModel):
    PAID_TYPE = (
        ("full_payment", "full_payment"),
        ("milestone", "milestone"),
        ("perHour", "perHour")
    )
    DURATION = (
        ("0-1 Month", "0-1 Month"),
        ("1-2 Months", "1-2 Months"),
        ("2-4 Months", "2-4 Months"),
        ("4-6 Months", "4-6 Months"),
        ("6 Months to 1 Year", "6 Months to 1 Year"),
        ("1 Year +", "1 Year +"),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_in_bid")
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="job_in_bid")
    title = models.CharField(max_length=500, null=True, blank=True)
    description = models.CharField(max_length=5000, null=True, blank=True)
    duration = models.CharField(max_length=100, choices=DURATION, null=True, blank=True)
    paid_type = models.CharField(max_length=30, choices=PAID_TYPE, default="Project")
    amount = models.CharField(max_length=50, null=True, blank=True)
    file = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class BidMileStone(SoftDeleteModel):
    STATUS = (
        ("Active", "Active"),
        ("Inactive", "Inactive"),
        ("Pending", "Pending"),
        ("Completed", "Completed"),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_in_bid_mile_stone")
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="job_in_bid_mile_stone")
    bid = models.ForeignKey(Bid, on_delete=models.CASCADE, related_name="bid_in_bid_mile_stone")
    description = models.CharField(max_length=500, null=True, blank=True)
    duration = models.CharField(max_length=100, null=True, blank=True)
    amount = models.CharField(max_length=500, null=True, blank=True)
    status = models.CharField(max_length=50, choices=STATUS, null=True, blank=True, default="Pending")
    end = models.DateTimeField(null=True, blank=True)
    file = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['pk']


class JobAnswer(SoftDeleteModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_in_job_answer")
    bid = models.ForeignKey(Bid, on_delete=models.CASCADE, related_name="bid_in_job_answer")
    question = models.ForeignKey(JobQuestions, on_delete=models.CASCADE, related_name="job_question_in_job_answer")
    answer = models.CharField(max_length=5000, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-id']