from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import *

router = SimpleRouter()
# router.register("api/category", CategoryView, basename="category")
router.register("api/service", ServiceView, basename="service")
router.register("api/service_question", ServiceQuestionView, basename="service_question")
router.register("api/service_answer", ServiceAnswerView, basename="service_answer")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "api/gallery/<int:id>",
        GalleryDestroyView.as_view({"delete": "gallery"}),
        name="gallery",
    ),
]
