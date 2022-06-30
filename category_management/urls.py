from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import *
router = SimpleRouter()
router.register("api/category", CategoryView, basename="category")

urlpatterns = [
    path("", include(router.urls)),
]
