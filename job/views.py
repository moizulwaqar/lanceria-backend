from rest_framework import viewsets, status, exceptions
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from rest_framework.response import Response
from .models import Job, JobQuestions
from .serializers import JobSerializer, SkillSerializer, CategorySerializer, JobListSerializer, UserJobListSerializer
from category_management.models import Category
from django.core.exceptions import PermissionDenied
from lanceria_backend.utils import PermissionsUtil
from user_profile.models import Skill
from bid.models import Bid
from django.db.models import Q
from django.utils.translation import gettext_lazy as _


class JobViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = JobSerializer
    queryset = Job.objects.all().order_by('-id')

    def create(self, request, *args, **kwargs):
        if request.user.role == "Employer" or request.user.is_superuser:
            serializer = self.get_serializer(data=request.data)
            try:
                serializer.is_valid(raise_exception=True)
            except Exception as e:
                error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                         "errors": e.args[0]}
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
            serializer.save(user=request.user)
            response = {"statusCode": 201, "error": False, "data": serializer.data,
                        "message": "Job has been posted successfully!"}
            return Response(response, status=status.HTTP_201_CREATED)
        raise exceptions.PermissionDenied()

    def list(self, request, *args, **kwargs):
        paginator = PageNumberPagination()
        paginator.page_size = 10
        result = paginator.paginate_queryset(self.queryset, request)
        serializer = self.serializer_class(result, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # PermissionsUtil.permission(request, instance)
        serializer = self.get_serializer(instance)
        response = {"statusCode": 200, "error": False, "data": serializer.data,
                    "message": "Job data!"}
        return Response(response, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        PermissionsUtil.permission(request, instance)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            error = {"success": False, "message": e.args[0], "data": ""}
            return Response(error)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}
        response = {"success": True, "message": "Job successfully updated!", "data": serializer.data}
        return Response(response, status=status.HTTP_200_OK)

    def perform_update(self, serializer):
        serializer.save()

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        PermissionsUtil.permission(request, instance)
        self.perform_destroy(instance)
        response = {"statusCode": 204, "error": False, "data": "",
                    "message": "Job Successfully deleted!"}
        return Response(response, status=status.HTTP_200_OK)

    def perform_destroy(self, instance):
        instance.delete()

    def user_job_list(self, request):
        paginator = PageNumberPagination()
        paginator.page_size = 10
        result = paginator.paginate_queryset(Job.objects.filter(user=self.request.user).order_by('-id'), request)
        serializer = UserJobListSerializer(result, many=True)
        return paginator.get_paginated_response(serializer.data)

    def job_list(self, request):
        paginator = PageNumberPagination()
        paginator.page_size = 10
        result = paginator.paginate_queryset(Job.objects.all().order_by('-id'), request)
        serializer = JobListSerializer(result, many=True)
        return paginator.get_paginated_response(serializer.data)

    def job_list_as_freelancer(self, request):
        if request.user.role == "Freelancer" or request.user.is_superuser:
            paginator = PageNumberPagination()
            paginator.page_size = 10
            bids = Bid.objects.filter(user=self.request.user).values_list("job", flat=True)
            result = paginator.paginate_queryset(Job.objects.all().exclude(Q(user=self.request.user) | Q(id__in=bids)).order_by('-id').order_by('-id'),
                                                 request)
            serializer = JobListSerializer(result, many=True)
            return paginator.get_paginated_response(serializer.data)
        raise exceptions.PermissionDenied()

    def get_permissions(self):
        # if self.action == "list":
        #     permission_classes = [IsAdminUser]
        #
        # # elif self.action == "create":
        # #     if self.request.user.role == "Employer" or self.request.user.is_superuser:
        # #         permission_classes = [IsAuthenticated]
        # #     else:
        # #         raise PermissionDenied()
        # else:
        permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def pre_data(self, request):
        category = Category.objects.filter(tn_ancestors_pks="").order_by("name")
        category_serializer = CategorySerializer(category, many=True)
        skills = Skill.objects.all().order_by("name")
        skill_serializer = SkillSerializer(skills, many=True)
        response = {"statusCode": 200, "error": False, "data": {"categories": category_serializer.data,
                                                                "skills": skill_serializer.data},
                    "message": "Get category and skills data!"}
        return Response(response, status=status.HTTP_200_OK)

    def child_category(self, request, *args, **kwargs):
        parent_id = self.kwargs.get("id")
        category = Category.objects.filter(tn_parent=parent_id).order_by("name")
        category_serializer = CategorySerializer(category, many=True)
        if not category_serializer.data:
            response = {"statusCode": 200, "error": False, "data": "",
                        "message": "No data found!"}
            return Response(response, status=status.HTTP_200_OK)
        response = {"statusCode": 200, "error": False, "data": category_serializer.data,
                    "message": "Child category data!"}
        return Response(response, status=status.HTTP_200_OK)

    def delete_job_question(self, request, id):
        if request.user.role == "Employer" or self.request.user.is_superuser:
            question = JobQuestions.objects.filter(id=id).exists()
            if question:
                question = JobQuestions.objects.filter(id=id)
                PermissionsUtil.permission(request, question.first())
                question.delete()
                response = {"statusCode": 200, "error": False,
                            "message": "Question successfully deleted!"}
                return Response(response, status=status.HTTP_200_OK)
            else:
                message = {"message": ["No Mile stone matches the given query!"]}
                response = {"statusCode": 404, "error": True, "data": "",
                            "message": "No Question matches the given query!", "errors": message}
                return Response(response, status=status.HTTP_404_NOT_FOUND)
        raise exceptions.PermissionDenied()