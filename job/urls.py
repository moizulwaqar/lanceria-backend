from rest_framework.routers import SimpleRouter, DefaultRouter
from .views import *
from django.urls import path, include


router = SimpleRouter()
router.register("api/job", JobViewSet, basename="job")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "api/user_job_list",
        JobViewSet.as_view({"get": "user_job_list"}),
        name="user_job_list",
    ),
    path(
        "api/job_list",
        JobViewSet.as_view({"get": "job_list"}),
        name="job_list",
    ),
    path(
        "api/job_list_as_freelancer",
        JobViewSet.as_view({"get": "job_list_as_freelancer"}),
        name="job_list_as_freelancer",
    ),
    path(
        "api/job_pre_data",
        JobViewSet.as_view({"get": "pre_data"}),
        name="job_pre_data",
    ),
    path(
        "api/child_category/<int:id>",
        JobViewSet.as_view({"get": "child_category"}),
        name="child_category",
    ),
    path(
        "api/job_question/<int:id>",
        JobViewSet.as_view({"delete": "delete_job_question"}),
        name="job_question",
    ),

]
