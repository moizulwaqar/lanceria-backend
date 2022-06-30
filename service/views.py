from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from rest_framework import status, exceptions
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from .models import Service, ServiceQuestion, ServiceAnswer, Gallery
from .serializers import ServiceSerializer, ServiceQuestionSerializer, ServiceAnswerSerializer, \
    UpdateServiceSerializer
from lanceria_backend.utils import PermissionsUtil
from rest_framework import viewsets


# Create your views here.


class ServiceView(viewsets.ModelViewSet):
    serializer_class = ServiceSerializer
    queryset = Service.objects.all().order_by('-id')

    def create(self, request, *args, **kwargs):
        if request.user.role == "Freelancer" or request.user.is_superuser:
            serializer = self.get_serializer(data=request.data)
            try:
                serializer.is_valid(raise_exception=True)
            except Exception as e:
                error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                         "errors": e.args[0]}
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
            serializer.save(user=request.user)
            response = {"statusCode": 201,  "error": False, "data": serializer.data,
                        "message": "Service successfully created!"}
            return Response(response, status=status.HTTP_201_CREATED)
        raise exceptions.PermissionDenied()

    def list(self, request, *args, **kwargs):
        paginator = PageNumberPagination()
        paginator.page_size = 4
        result = paginator.paginate_queryset(Service.objects.filter(user=self.request.user).order_by("-id"), request)
        serializer = self.serializer_class(result, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        response = {"statusCode": 200, "error": False, "data": serializer.data,
                    "message": "Get data!"}
        return Response(response, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        if request.user.role == "Freelancer" or request.user.is_superuser:
            serializer = UpdateServiceSerializer(instance, data=request.data, partial=partial, context={'user': request.user})
            PermissionsUtil.permission(request, instance)
            try:
                serializer.is_valid(raise_exception=True)
            except Exception as e:
                error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                         "errors": e.args[0]}
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
            self.perform_update(serializer)

            if getattr(instance, '_prefetched_objects_cache', None):
                instance._prefetched_objects_cache = {}
            response = {"statusCode": 200, "error": False, "data": serializer.data,
                        "message": "Service successfully updated!"}
            return Response(response, status=status.HTTP_200_OK)
        raise exceptions.PermissionDenied()

    def perform_update(self, serializer):
        serializer.save()

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        PermissionsUtil.permission(request, instance)
        self.perform_destroy(instance)
        response = {"statusCode": 200, "error": False, "data": "",
                    "message": "Service successfully deleted!"}
        return Response(response, status=status.HTTP_200_OK)

    def perform_destroy(self, instance):
        instance.delete()

    def get_permissions(self):
        permission_classes = [IsAuthenticated] or [IsAdminUser]
        return [permission() for permission in permission_classes]


class ServiceQuestionView(viewsets.ModelViewSet):
    serializer_class = ServiceQuestionSerializer
    queryset = ServiceQuestion.objects.all().order_by('-id')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            error = {"success": False, "message": e.args[0], "data": ""}
            return Response(error)
        serializer.save(user=request.user)
        response = {"success": True, "message": "Service Question successfully created!", "data": serializer.data}
        return Response(response, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        paginator = PageNumberPagination()
        paginator.page_size = 10
        result = paginator.paginate_queryset(self.queryset, request)
        serializer = self.serializer_class(result, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        response = {"success": True, "message": "Get data!", "data": serializer.data}
        return Response(response, status=status.HTTP_200_OK)

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
            instance._prefetched_objects_cache = {}
        response = {"success": True, "message": "Service Question successfully updated!", "data": serializer.data}
        return Response(response, status=status.HTTP_200_OK)

    def perform_update(self, serializer):
        serializer.save()

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        PermissionsUtil.permission(request, instance)
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        PermissionsUtil.permission(request, instance)
        self.perform_destroy(instance)
        response = {"success": True, "message": "Service Question successfully deleted!", "data": ""}
        return Response(response, status=status.HTTP_200_OK)

    def perform_destroy(self, instance):
        instance.delete()

    def get_permissions(self):
        if self.action in ["retrieve"]:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated] or [IsAdminUser]
        return [permission() for permission in permission_classes]


class ServiceAnswerView(viewsets.ModelViewSet):
    serializer_class = ServiceAnswerSerializer
    queryset = ServiceAnswer.objects.all().order_by('-id')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            error = {"success": False, "message": e.args[0], "data": ""}
            return Response(error)
        serializer.save(user=request.user)
        response = {"success": True, "message": "Service Answer successfully created!", "data": serializer.data}
        return Response(response, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        paginator = PageNumberPagination()
        paginator.page_size = 10
        result = paginator.paginate_queryset(self.queryset, request)
        serializer = self.serializer_class(result, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        response = {"success": True, "message": "Get data!", "data": serializer.data}
        return Response(response, status=status.HTTP_200_OK)

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
            instance._prefetched_objects_cache = {}
        response = {"success": True, "message": "Service Answer successfully updated!", "data": serializer.data}
        return Response(response, status=status.HTTP_200_OK)

    def perform_update(self, serializer):
        serializer.save()

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        PermissionsUtil.permission(request, instance)
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        PermissionsUtil.permission(request, instance)
        self.perform_destroy(instance)
        response = {"success": True, "message": "Service Answer successfully deleted!", "data": ""}
        return Response(response, status=status.HTTP_200_OK)

    def perform_destroy(self, instance):
        instance.delete()

    def get_permissions(self):
        if self.action in ["retrieve"]:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated] or [IsAdminUser]
        return [permission() for permission in permission_classes]


class GalleryDestroyView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def gallery(self, request, id):
        if request.user.role == "Freelancer" or request.user.is_superuser:
            if Gallery.objects.filter(id=id).exists():
                Gallery.objects.filter(id=id).delete()
                response = {"statusCode": 200, "error": False,
                            "message": "Gallery successfully deleted!"}
                return Response(response, status=status.HTTP_200_OK)
            else:
                message = {"message": ["No Gallery matches the given query!"]}
                response = {"statusCode": 404, "error": True, "data": "",
                            "message": "No Gallery matches the given query!", "errors": message}
                return Response(response, status=status.HTTP_404_NOT_FOUND)
        raise exceptions.PermissionDenied()
