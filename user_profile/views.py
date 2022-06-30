from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import exceptions
from rest_framework.views import APIView
from authentication.models import UserProfile, User
from lanceria_backend.utils import PermissionsUtil
# from .models import User
from .models import Skill, Education, Experience, Portfolio, LinkedAccount, Language, Certification, UserSkill
from .serializers import SkillSerializer, FreelancerProfileSerializer, UserEducationSerializer, \
    UserExperienceSerializer, UserPortfolioSerializer, LinkedAccountSerializer, LanguageSerializer, \
    CertificationSerializer, ProfileListSerializer, ViewFreelancerProfile, EmployerProfileSerializer, \
    UserSkillSerializer, FreelancerDashboardSerializer, EmployerDashboardSerializer, GetFreelancerProfileSerializer, \
    GetEmployerProfileSerializer, ListOfSkillSerializer, UpdateProfileSerializer, UpdateLanguageSerializer
from authentication.serializers import FreelancerViewSerializer, EmployerViewSerializer
from .degree import degree
from .countries import countries
# Create your views here.


class ProfileSetup(viewsets.ModelViewSet):
    queryset = User.objects.all()

    def create(self, request, *args, **kwargs):
        return Response({'post': "Method is not allowed"})

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        if instance.email_verified:
            verify = True
        else:
            verify = False
        if request.user.id == instance.id or request.user.is_superuser:
            if request.user.role == "Freelancer":
                serializer = FreelancerProfileSerializer(instance, data=request.data, partial=partial)
            else:
                serializer = EmployerProfileSerializer(instance, data=request.data, partial=partial)
            try:
                serializer.is_valid(raise_exception=True)
            except Exception as e:
                error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                         "errors": e.args[0]}
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
            self.perform_update(serializer, verify)

            if getattr(instance, '_prefetched_objects_cache', None):
                # If 'prefetch_related' has been applied to a queryset, we need to
                # forcibly invalidate the prefetch cache on the instance.
                instance._prefetched_objects_cache = {}
            profile_serializer = UpdateProfileSerializer(data=request.data)

            try:
                profile_serializer.is_valid(raise_exception=True)
            except Exception as e:
                error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                         "errors": e.args[0]}
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
            profile = UserProfile.objects.filter(user=instance, role=instance.role)
            if profile:
                profile_serializer = UpdateProfileSerializer(profile.first(), data=request.data, partial=partial)
                try:
                    profile_serializer.is_valid(raise_exception=True)
                except Exception as e:
                    error = {"statusCode": 400, "error": True, "data": "",
                             "message": "Bad Request, Please check request",
                             "errors": e.args[0]}
                    return Response(error, status=status.HTTP_400_BAD_REQUEST)
            else:
                profile_serializer.save(user=instance, role=instance.role)
            profile_serializer.save()
            response = {"statusCode": 200, "error": False,
                        "data": dict(serializer.data, **UpdateProfileSerializer(
                        UserProfile.objects.filter(user=instance, role=instance.role).first()).data),
                        "message": "Successfully Updated!"}
            return Response(response, status=status.HTTP_200_OK)
        raise exceptions.PermissionDenied()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.role == "Freelancer":
            serializer = FreelancerViewSerializer(instance)
        else:
            serializer = EmployerViewSerializer(instance)
        profile = UserProfile.objects.filter(user=instance, role=instance.role)
        if profile:
            profile_data = UpdateProfileSerializer(profile.first()).data
        else:
            profile_data = {"skill": "", "title": "", "description": ""}
        response = {"statusCode": 200, "error": False, "data": dict(serializer.data, **profile_data),
                    "message": "Profile Data!"}
        return Response(response, status=status.HTTP_200_OK)
        # return Response(serializer.data)

    def perform_update(self, serializer, verify):
        serializer.save(email_verified=verify)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        paginator = PageNumberPagination()
        paginator.page_size = 10
        result = paginator.paginate_queryset(User.objects.all().exclude(is_superuser=True), request)
        serializer = ProfileListSerializer(result, many=True)
        return paginator.get_paginated_response(serializer.data)

    def employer_list(self, request, *args, **kwargs):
        paginator = PageNumberPagination()
        paginator.page_size = 10
        result = paginator.paginate_queryset(User.objects.filter(role="Employer"), request)
        serializer = ProfileListSerializer(result, many=True)
        return paginator.get_paginated_response(serializer.data)

    def freelancer_list(self, request, *args, **kwargs):
        paginator = PageNumberPagination()
        paginator.page_size = 10
        result = paginator.paginate_queryset(User.objects.filter(role="Freelancer"), request)
        serializer = ProfileListSerializer(result, many=True)
        return paginator.get_paginated_response(serializer.data)

    def dashboard(self, request, *args, **kwargs):
        instance = request.user
        if instance.role == "Freelancer":
            serializer = FreelancerDashboardSerializer(instance)
        else:
            serializer = EmployerDashboardSerializer(instance, context={'request': request})
        response = {"statusCode": 200, "error": False, "message": "Get Data!", "data": serializer.data}
        return Response(response, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.is_superuser:
            raise exceptions.PermissionDenied()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_200_OK)

    def get_permissions(self):
        if self.action in ["destroy", "list", 'employer_list', "freelancer_list"]:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]


class SkillViewSet(viewsets.ModelViewSet):
    # permission_classes = [IsAdminUser]
    serializer_class = SkillSerializer
    queryset = Skill.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            error = {"success": False, "message": e.args[0], "data": ""}
            return Response(error)
        serializer.save()
        response = {"success": True, "message": "Skill successfully created!", "data": serializer.data}
        return Response(response, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        # paginator = PageNumberPagination()
        # paginator.page_size = 10
        # result = paginator.paginate_queryset(self.queryset, request)
        result = Skill.objects.all()
        serializer = ListOfSkillSerializer(result, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        response = {"success": True, "message": "Get data!", "data": serializer.data}
        return Response(response, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
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
        response = {"success": True, "message": "Skill successfully updated!", "data": serializer.data}
        return Response(response, status=status.HTTP_200_OK)

    def perform_update(self, serializer):
        serializer.save()

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        response = {"success": True, "message": "Skill successfully deleted!", "data": ""}
        return Response(response, status=status.HTTP_200_OK)

    def perform_destroy(self, instance):
        instance.delete()

    def get_permissions(self):
        if self.action in ["list"]:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]


class UserEducation(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = UserEducationSerializer
    queryset = Education.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                     "errors": e.args[0]}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        serializer.save(user=request.user)
        response = {"statusCode": 201, "error": False, "data": serializer.data,
                    "message": "Education successfully created!"}
        return Response(response, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        PermissionsUtil.permission(request, instance)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                     "errors": e.args[0]}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}
        response = {"statusCode": 200, "error": False, "data": serializer.data,
                    "message": "Education successfully updated!"}
        return Response(response, status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        paginator = PageNumberPagination()
        paginator.page_size = 10
        result = paginator.paginate_queryset(Education.objects.filter(user=request.user).order_by("-id"), request)
        serializer = self.serializer_class(result, many=True)
        return paginator.get_paginated_response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        PermissionsUtil.permission(request, instance)
        serializer = self.get_serializer(instance)
        response = {"statusCode": 200, "error": False, "data": serializer.data,
                    "message": "Get data!"}
        return Response(response, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        PermissionsUtil.permission(request, instance)
        self.perform_destroy(instance)
        response = {"statusCode": 204, "error": False, "data": "",
                    "message": "Education successfully deleted!"}
        return Response(response, status=status.HTTP_200_OK)

    def perform_destroy(self, instance):
        instance.delete()


class UserExperience(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = UserExperienceSerializer
    queryset = Experience.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                     "errors": e.args[0]}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        serializer.save(user=request.user)
        response = {"statusCode": 201, "error": False, "data": serializer.data,
                    "message": "Experience successfully created!"}
        return Response(response, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        PermissionsUtil.permission(request, instance)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                     "errors": e.args[0]}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}
        response = {"statusCode": 200, "error": False, "data": serializer.data,
                    "message": "Experience successfully updated!"}
        return Response(response, status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        paginator = PageNumberPagination()
        paginator.page_size = 10
        result = paginator.paginate_queryset(Experience.objects.filter(user=request.user).order_by("-id"), request)
        serializer = self.serializer_class(result, many=True)
        return paginator.get_paginated_response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        PermissionsUtil.permission(request, instance)
        serializer = self.get_serializer(instance)
        response = {"statusCode": 200, "error": False, "data": serializer.data,
                    "message": "Get data!"}
        return Response(response, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        PermissionsUtil.permission(request, instance)
        self.perform_destroy(instance)
        response = {"statusCode": 204, "error": False, "data": "",
                    "message": "Experience successfully delete!"}
        return Response(response, status=status.HTTP_200_OK)

    def perform_destroy(self, instance):
        instance.delete()


class UserPortfolio(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = UserPortfolioSerializer
    queryset = Portfolio.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            error = {"success": False, "message": e.args[0], "data": ""}
            return Response(error)
        serializer.save(user=request.user)
        response = {"success": True, "message": "Portfolio successfully created!", "data": serializer.data}
        return Response(response, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        PermissionsUtil.permission(request, instance)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
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
        response = {"success": True, "message": "Portfolio successfully updated!", "data": serializer.data}
        return Response(response, status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        paginator = PageNumberPagination()
        paginator.page_size = 10
        result = paginator.paginate_queryset(Portfolio.objects.filter(user=request.user).order_by("-id"), request)
        serializer = self.serializer_class(result, many=True)
        return paginator.get_paginated_response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        PermissionsUtil.permission(request, instance)
        serializer = self.get_serializer(instance)
        response = {"success": True, "message": "Get data!", "data": serializer.data}
        return Response(response, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        PermissionsUtil.permission(request, instance)
        self.perform_destroy(instance)
        response = {"success": True, "message": "Portfolio successfully deleted!", "data": ""}
        return Response(response, status=status.HTTP_200_OK)

    def perform_destroy(self, instance):
        instance.delete()


class LinkedAccountView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = LinkedAccountSerializer
    queryset = LinkedAccount.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                     "errors": e.args[0]}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        serializer.save(user=request.user)
        response = {"statusCode": 201, "error": False, "data": serializer.data,
                    "message": "Link account successfully created!"}
        return Response(response, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        PermissionsUtil.permission(request, instance)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                     "errors": e.args[0]}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}
        response = {"statusCode": 200, "error": False, "data": serializer.data,
                    "message": "Link account successfully updated!"}
        return Response(response, status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        paginator = PageNumberPagination()
        paginator.page_size = 10
        result = paginator.paginate_queryset(LinkedAccount.objects.filter(user=request.user).order_by("-id"), request)
        serializer = self.serializer_class(result, many=True)
        return paginator.get_paginated_response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        PermissionsUtil.permission(request, instance)
        serializer = self.get_serializer(instance)
        response = {"statusCode": 200, "error": False, "data": serializer.data,
                    "message": "Get data"}
        return Response(response, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        PermissionsUtil.permission(request, instance)
        self.perform_destroy(instance)
        response = {"statusCode": 204, "error": False, "data": "",
                    "message": "Link account successfully deleted!"}
        return Response(response, status=status.HTTP_200_OK)

    def perform_destroy(self, instance):
        instance.delete()


class LanguageView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = LanguageSerializer
    queryset = Language.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'user': request.user})
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                     "errors": e.args[0]}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        serializer.save(user=request.user)
        response = {"statusCode": 201, "error": False, "data": serializer.data,
                    "message": "Language create successfully!"}
        return Response(response, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        PermissionsUtil.permission(request, instance)
        serializer = UpdateLanguageSerializer(instance, data=request.data, partial=partial, context={'user': request.user,
                                                                                                'instance': instance})
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                     "errors": e.args[0]}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}
        response = {"statusCode": 200, "error": False, "data": serializer.data,
                    "message": "Language successfully updated!"}
        return Response(response, status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        paginator = PageNumberPagination()
        paginator.page_size = 10
        result = paginator.paginate_queryset(Language.objects.filter(user=request.user).order_by("-id"), request)
        serializer = self.serializer_class(result, many=True)
        return paginator.get_paginated_response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        PermissionsUtil.permission(request, instance)
        serializer = self.get_serializer(instance)
        name = {"value": serializer.data.get('name'), "label": serializer.data.get('name')}
        level = {"value": serializer.data.get('level'), "label": serializer.data.get('level')}
        data = {"name": name, "level": level}
        response = {"statusCode": 200, "error": False, "data": data,
                    "message": "Get data!"}
        return Response(response, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        PermissionsUtil.permission(request, instance)
        self.perform_destroy(instance)
        response = {"statusCode": 200, "error": False, "data": "",
                    "message": "Language successfully deleted!"}
        return Response(response, status=status.HTTP_200_OK)

    def perform_destroy(self, instance):
        instance.delete()


# class UserSkillView(viewsets.ModelViewSet):


#     permission_classes = [IsAuthenticated]
#     serializer_class = UserSkillSerializer
#     queryset = UserSkill.objects.all()
#
#     def create(self, request, *args, **kwargs):
#         if UserSkill.objects.filter(user=request.user).exists():
#             error = {"statusCode": 400, "error": True, "data": "", "message": "You already created!"}
#             return Response(error, status=status.HTTP_400_BAD_REQUEST)
#         serializer = self.get_serializer(data=request.data)
#         try:
#             serializer.is_valid(raise_exception=True)
#         except Exception as e:
#             error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
#                      "errors": e.args[0]}
#             return Response(error, status=status.HTTP_400_BAD_REQUEST)
#         serializer.save(user=request.user)
#         response = {"statusCode": 201, "error": False, "data": serializer.data,
#                     "message": "User Skill create successfully!"}
#         return Response(response, status=status.HTTP_201_CREATED)
#
#     def update(self, request, *args, **kwargs):
#         partial = kwargs.pop('partial', False)
#         instance = self.get_object()
#         PermissionsUtil.permission(request, instance)
#         serializer = self.get_serializer(instance, data=request.data, partial=partial)
#         try:
#             serializer.is_valid(raise_exception=True)
#         except Exception as e:
#             error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
#                      "errors": e.args[0]}
#             return Response(error, status=status.HTTP_400_BAD_REQUEST)
#         self.perform_update(serializer)
#
#         if getattr(instance, '_prefetched_objects_cache', None):
#             # If 'prefetch_related' has been applied to a queryset, we need to
#             # forcibly invalidate the prefetch cache on the instance.
#             instance._prefetched_objects_cache = {}
#         response = {"statusCode": 200, "error": False, "data": serializer.data,
#                     "message": "User skill successfully updated!"}
#         return Response(response, status=status.HTTP_200_OK)
#
#     def list(self, request, *args, **kwargs):
#         paginator = PageNumberPagination()
#         paginator.page_size = 10
#         result = paginator.paginate_queryset(UserSkill.objects.filter(user=request.user).order_by("-id"), request)
#         serializer = self.serializer_class(result, many=True)
#         return paginator.get_paginated_response(serializer.data)
#
#     def perform_update(self, serializer):
#         serializer.save()
#
#     def partial_update(self, request, *args, **kwargs):
#         kwargs['partial'] = True
#         return self.update(request, *args, **kwargs)
#
#     def retrieve(self, request, *args, **kwargs):
#         instance = self.get_object()
#         PermissionsUtil.permission(request, instance)
#         serializer = self.get_serializer(instance)
#         response = {"statusCode": 200, "error": False, "data": serializer.data,
#                     "message": "Get data!"}
#         return Response(response, status=status.HTTP_200_OK)
#
#     def destroy(self, request, *args, **kwargs):
#         instance = self.get_object()
#         PermissionsUtil.permission(request, instance)
#         self.perform_destroy(instance)
#         response = {"statusCode": 200, "error": False, "data": "",
#                     "message": "User skill successfully deleted!"}
#         return Response(response, status=status.HTTP_204_NO_CONTENT)
#
#     def perform_destroy(self, instance):
#         instance.delete()


class UserSkillView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def user_skill(self, request):
        if not UserSkill.objects.filter(user=self.request.user).exists():
            serializer = UserSkillSerializer(data=request.data)
            try:
                serializer.is_valid(raise_exception=True)
            except Exception as e:
                error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                         "errors": e.args[0]}
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
            serializer.save(user=request.user)
            response = {"statusCode": 201, "error": False, "data": serializer.data,
                        "message": "User skill successfully updated!"}
            return Response(response, status=status.HTTP_201_CREATED)
        else:
            instance = UserSkill.objects.filter(user=self.request.user).first()
            PermissionsUtil.permission(request, instance)
            serializer = UserSkillSerializer(instance, data=request.data)
            try:
                serializer.is_valid(raise_exception=True)
            except Exception as e:
                error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                         "errors": e.args[0]}
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            response = {"statusCode": 200, "error": False, "data": serializer.data,
                        "message": "User skill successfully updated!"}
            return Response(response, status=status.HTTP_200_OK)


class CertificationView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CertificationSerializer
    queryset = Certification.objects.all().order_by('-id')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            error = {"success": False, "message": e.args[0], "data": ""}
            return Response(error)
        serializer.save(user=request.user)
        response = {"success": True, "message": "Certification successfully created!", "data": serializer.data}
        return Response(response, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        PermissionsUtil.permission(request, instance)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
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
        response = {"success": True, "message": "Certification successfully updated!", "data": serializer.data}
        return Response(response, status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        paginator = PageNumberPagination()
        paginator.page_size = 10
        result = paginator.paginate_queryset(Certification.objects.filter(user=request.user).order_by("-id"), request)
        serializer = self.serializer_class(result, many=True)
        return paginator.get_paginated_response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        PermissionsUtil.permission(request, instance)
        serializer = self.get_serializer(instance)
        response = {"success": True, "message": "Get data!", "data": serializer.data}
        return Response(response, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        PermissionsUtil.permission(request, instance)
        self.perform_destroy(instance)
        response = {"success": True, "message": "Certification successfully deleted!", "data": ""}
        return Response(response, status=status.HTTP_200_OK)

    def perform_destroy(self, instance):
        instance.delete()


class UsersDelete(APIView):
    permission_classes = (IsAdminUser,)

    def delete(self, request):
        try:
            ids = request.data.get('ids')
            if not ids:
                message = {"message": {"user ids required"}}
                error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                         "errors": message}
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
            users_not_found = []
            users_exists = []
            for user_id in ids:
                user_obj_check = User.objects.filter(id=user_id).exists()
                if not user_obj_check:
                    users_not_found.append(user_id)
                if user_obj_check:
                    users_exists.append(user_id)
                User.objects.filter(id=user_id).delete()
            message_not_exists = {"user_ids": ["Object with ids={} does not exist.".format(users_not_found)]}
            message_exists = {"user_ids": ["Object with ids={} deleted successfully.".format(users_exists)]}
            response = {"statusCode": 200, "error": False,
                        "not_found": message_not_exists, "message": message_exists}
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                     "errors": e.args[0]}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)


class DegreeList(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            response = {"statusCode": 200, "error": False, "data": degree, "message": "Degrees Detail!"}
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                     "errors": e.args[0]}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)


class CountriesList(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            response = {"statusCode": 200, "error": False, "data": countries, "message": "Countires Detail!"}
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                     "errors": e.args[0]}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
