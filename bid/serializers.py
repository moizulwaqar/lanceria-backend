from django.db import transaction
from rest_framework import serializers
from rest_framework import exceptions
from job.models import Job, JobQuestions
from .models import Bid, BidMileStone, JobAnswer


class BidMileStoneSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    job = serializers.SlugRelatedField(queryset=Job.objects.all(), slug_field='id', required=False)
    bid = serializers.SlugRelatedField(queryset=Bid.objects.all(), slug_field='id', required=False)
    end = serializers.DateTimeField(required=False)

    class Meta:
        model = BidMileStone
        fields = ["id", "bid", "job", "description", "duration", "amount", "status", "end", "file"]

    def to_internal_value(self, data):
        if data.get('end', None) == '':
            data.pop('end')
        return super(BidMileStoneSerializer, self).to_internal_value(data)


class BidMileStoneValidationSerializer(serializers.ModelSerializer):
    STATUS = (
        ("Active", "Active"),
        ("Inactive", "Inactive"),
        ("Pending", "Pending"),
        ("Completed", "Completed"),
    )
    id = serializers.IntegerField(required=False)
    description = serializers.CharField(required=True, max_length=500)
    amount = serializers.CharField(required=True, max_length=500)
    end = serializers.DateTimeField(required=True)
    status = serializers.ChoiceField(choices=STATUS, required=False)
    duration = serializers.CharField(required=False, max_length=100, allow_blank=True)
    file = serializers.URLField(required=False, allow_blank=True)

    class Meta:
        model = BidMileStone
        fields = ["id", "description", "duration", "amount", "status", "end", "file"]


class JobAnswerSerializer(serializers.ModelSerializer):
    question = serializers.SlugRelatedField(queryset=JobQuestions.objects.all(), slug_field='id')
    ques = serializers.CharField(read_only=True, source="question.question")
    answer = serializers.CharField(max_length=5000)
    class Meta:
        model = JobAnswer
        fields = ["id", "question", "ques", "answer"]


class BidSerializer(serializers.ModelSerializer):
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
    job = serializers.SlugRelatedField(queryset=Job.objects.all(), slug_field='id', required=True)
    title = serializers.CharField(required=False, max_length=500, allow_blank=True)
    description = serializers.CharField(required=True, max_length=5000)
    duration = serializers.ChoiceField(choices=DURATION, required=True)
    paid_type = serializers.ChoiceField(choices=PAID_TYPE, required=True)
    amount = serializers.CharField(required=False, max_length=500, allow_blank=True)
    mile_stones = BidMileStoneSerializer(many=True, required=False, source="bid_in_bid_mile_stone")
    job_answers = serializers.SerializerMethodField()
    file = serializers.URLField(required=False, allow_blank=True)

    class Meta:
        model = Bid
        fields = ["id", "job", "title", "description", "duration", "paid_type", "amount", "file", "mile_stones", "job_answers"]

    def get_job_answers(self, obj):
        job = obj.job
        question_ids = JobQuestions.objects.filter(job=job).values_list("id", flat=True)
        job_answers = JobAnswer.objects.filter(question__in=question_ids, bid=obj, user=obj.user)
        serializer = JobAnswerSerializer(job_answers, many=True)
        return serializer.data


    def create(self, validated_data):
        job_answers = self.context["request"].data.get("job_answers")
        job = validated_data.get('job')
        user = validated_data.get('user')
        paid_type = validated_data.get('paid_type')
        milestones_data = validated_data.pop('bid_in_bid_mile_stone', [])
        if job.user == user:
            raise exceptions.PermissionDenied()
        if paid_type == "milestone" and not milestones_data:
            errors = {"mile_stones": ["Please add at least one milestone"]}
            raise serializers.ValidationError({"statusCode": 400, "error": True,
                                               "data": "", "message": "Bad Request, Please check request",
                                               "errors": errors})
        check_bid = Bid.objects.filter(job=job, user=user).exists()
        if check_bid:
            errors = {"message": ["You have already bid on this job"]}
            raise serializers.ValidationError({"statusCode": 400, "error": True, "data": "",
                                               "message": "Bad Request, Please check request",
                                               "errors": errors})
        if (paid_type == "full_payment" and not self.context["request"].data.get("amount")) or \
                (paid_type == "perHour" and not self.context["request"].data.get("amount")):
            errors = {"amount": ["This field is required"]}
            raise serializers.ValidationError({"statusCode": 400, "error": True,
                                               "data": "", "message": "Bad Request, Please check request",
                                               "errors": errors})
        with transaction.atomic():
            if paid_type == "milestone":
                mile_stone_validation = BidMileStoneValidationSerializer(data=milestones_data, many=True)
                try:
                    mile_stone_validation.is_valid(raise_exception=True)
                except Exception as e:
                    raise serializers.ValidationError({"statusCode": 400, "error": True, "data": "",
                                                       "message": "Bad Request, Please check request",
                                                       "errors": {"mile_stones": e.args[0]}})
            bid = Bid.objects.create(**validated_data)
            if paid_type == "milestone":
                bid.amount = ""
                bid.save()
                for milestone_data in milestones_data:
                    milestone_data.pop('job', '')
                    milestone_data.pop('bid', '')
                    BidMileStone.objects.create(bid=bid,  user=user, job=job, **milestone_data)
            if job_answers:
                job_answer_serializer = JobAnswerSerializer(data=job_answers, many=True)
                try:
                    job_answer_serializer.is_valid(raise_exception=True)
                except Exception as e:
                    raise serializers.ValidationError({"statusCode": 400, "error": True, "data": "",
                                                       "message": "Bad Request, Please check request",
                                                       "errors": {"job_answers": e.args[0]}})
                job_answer_serializer.save(user=user, bid=bid)
            return bid

    def update(self, instance, validated_data):
        milestones = validated_data.pop('bid_in_bid_mile_stone', [])
        with transaction.atomic():
            if 'paid_type' in validated_data:
                if validated_data.get('paid_type') == 'full_payment':
                    BidMileStone.objects.filter(bid=instance).delete()

                elif validated_data.get('paid_type') == 'milestone':
                    if not milestones and not self.partial:
                        errors = {"mile_stones": ["Please add at least one milestone"]}
                        raise serializers.ValidationError({"statusCode": 400, "error": True,
                                                           "data": "", "message": "Bad Request, Please check request",
                                                           "errors": errors})

            if validated_data.get('paid_type') == 'milestone' or self.partial:
                for milestone in milestones:
                    milestone_id = milestone.get('id', None)
                    milestone.pop('job', '')
                    milestone.pop('bid', '')
                    if milestone_id:
                        BidMileStone.objects.filter(id=milestone_id, bid=instance).update(**milestone)
                    else:
                        mile_stone_validation = BidMileStoneValidationSerializer(data=milestones, many=True)
                        try:
                            mile_stone_validation.is_valid(raise_exception=True)
                        except Exception as e:
                            raise serializers.ValidationError({"statusCode": 400, "error": True, "data": "",
                                                               "message": "Bad Request, Please check request",
                                                               "errors": {"mile_stones": e.args[0]}})
                        if not self.partial:
                            BidMileStone.objects.create(**milestone, job=instance.job, bid=instance,
                                                        user=instance.user)
            validated_data.pop('job', '')
            instance = super(BidSerializer, self).update(instance, validated_data)
            return instance
