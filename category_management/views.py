from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from .models import Category
from .serializers import CategorySerializer
# Create your views here.


class CategoryView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Category.objects.all().order_by('-id')
    serializer_class = CategorySerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                     "errors": e.args[0]}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        serializer.save(user=request.user)
        response = {"statusCode": 200, "error": False, "data": serializer.data,
                    "message": "Category successfully created!"}
        return Response(response, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
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
                    "message": "Category successfully updated!"}
        return Response(response, status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        paginator = PageNumberPagination()
        paginator.page_size = 10
        result = paginator.paginate_queryset(Category.objects.filter(user=request.user).order_by("-id"), request)
        serializer = self.serializer_class(result, many=True)
        return paginator.get_paginated_response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        response = {"statusCode": 200, "error": False, "data": serializer.data, "message": "Get data!"}
        return Response(response, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        response = {"statusCode": 200, "error": False, "message": "Category successfully deleted!"}
        return Response(response, status=status.HTTP_200_OK)

    def perform_destroy(self, instance):
        instance.delete()
