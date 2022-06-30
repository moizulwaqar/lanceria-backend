from rest_framework import viewsets, status, exceptions
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Bid, BidMileStone
from .serializers import BidSerializer, BidMileStoneSerializer
from django.core.exceptions import PermissionDenied
from lanceria_backend.utils import PermissionsUtil

# Create your views here.


class BidViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = BidSerializer
    queryset = Bid.objects.all()

    def create(self, request, *args, **kwargs):
        if self.request.user.role == "Freelancer" or self.request.user.is_superuser:
            serializer = self.get_serializer(data=request.data)
            try:
                serializer.is_valid(raise_exception=True)
            except Exception as e:
                error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                         "errors": e.args[0]}
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
            serializer.save(user=request.user)
            response = {"statusCode": 201, "error": False, "message": "Bid Submitted Successfully!",
                        "data": serializer.data}
            return Response(response, status=status.HTTP_201_CREATED)
        raise exceptions.PermissionDenied()

    def list(self, request, *args, **kwargs):
        paginator = PageNumberPagination()
        paginator.page_size = 10
        result = paginator.paginate_queryset(Bid.objects.filter(user=request.user), request)
        serializer = self.serializer_class(result, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        PermissionsUtil.permission(request, instance)
        serializer = self.get_serializer(instance)
        response = {"statusCode": 200, "error": False, "message": "Get data!", "data": serializer.data}
        return Response(response, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        PermissionsUtil.permission(request, instance)
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
        response = {"statusCode": 200, "error": False, "message": "Bid successfully updated!", "data": serializer.data}
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
        response = {"statusCode": 200, "error": False, "message": "Bid successfully deleted!", "data": ""}
        return Response(response, status=status.HTTP_200_OK)

    def perform_destroy(self, instance):
        instance.delete()

    def bids_on_job(self, request):
        paginator = PageNumberPagination()
        paginator.page_size = 10
        job = self.request.data.get('job_id')
        result = paginator.paginate_queryset(Bid.objects.filter(job=job), request)
        serializer = self.serializer_class(result, many=True)
        return paginator.get_paginated_response(serializer.data)


# class BidMileStoneViewSet(viewsets.ModelViewSet):
#     permission_classes = [IsAuthenticated]
#     serializer_class = BidMileStoneSerializer
#     queryset = BidMileStone.objects.all()
#
#     def destroy(self, request, *args, **kwargs):
#         instance = self.get_object()
#         PermissionsUtil.permission(request, instance)
#         self.perform_destroy(instance)
#         response = {"statusCode": 200, "error": False, "message": "Milestone successfully deleted!", "data": ""}
#         return Response(response, status=status.HTTP_200_OK)
#
#     def perform_destroy(self, instance):
#         instance.delete()


class BidMileStoneViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def destroy(self, request, id):
        if request.user.role == "Freelancer" or request.user.is_superuser:
            mile_stone = BidMileStone.objects.filter(id=id).exists()
            if mile_stone:

                mile_stone = BidMileStone.objects.filter(id=id)
                PermissionsUtil.permission(request, mile_stone.first())
                mile_stone.delete()
                response = {"statusCode": 200, "error": False,
                            "message": "Mile stone successfully deleted!"}
                return Response(response, status=status.HTTP_200_OK)
            else:
                message = {"message": ["No Mile stone matches the given query!"]}
                response = {"statusCode": 404, "error": True, "data": "",
                            "message": "No Mile stone matches the given query!", "errors": message}
                return Response(response, status=status.HTTP_404_NOT_FOUND)
        raise exceptions.PermissionDenied()