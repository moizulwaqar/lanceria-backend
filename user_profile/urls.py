from django.urls import path, include
from rest_framework.routers import SimpleRouter, DefaultRouter
from .views import *
router = SimpleRouter()
router.register("api/skill", SkillViewSet, basename="skill_url")
router.register("api/education", UserEducation, basename="education")
router.register("api/experience", UserExperience, basename="experience")
router.register("api/portfolio", UserPortfolio, basename="portfolio")
router.register("api/linked_account", LinkedAccountView, basename="linked_account")
router.register("api/language", LanguageView, basename="language")
router.register("api/certification", CertificationView, basename="certification")
router.register("api/profile", ProfileSetup, basename="profile")
# router.register("api/user_skill", UserSkillView, basename="user_skill")
# router.register("api/dashboard", UserSkillView, basename="dashboard")
urlpatterns = [
    path("", include(router.urls)),
    # path(
    #     "api/profile",
    #     ProfileSetup.as_view({"put": "update"}),
    #     name="update",
    # ),
    # path(
    #     "api/all_user",
    #     ProfileSetup.as_view({"get": "list"}),
    #     name="all_user",
    # ),
    path(
        "api/all_employer",
        ProfileSetup.as_view({"get": "employer_list"}),
        name="all_employer",
    ),
    path(
        "api/all_freelancer",
        ProfileSetup.as_view({"get": "freelancer_list"}),
        name="all_freelancer",
    ),
    path(
        "api/dashboard",
        ProfileSetup.as_view({"get": "dashboard"}),
        name="dashboard",
    ),

    path(
        "api/user_skill",
        UserSkillView.as_view({"post": "user_skill"}),
        name="user_skill",
    ),
    # path(
    #     "api/user/delete/<int:id>/",
    #     ProfileSetup.as_view({"get": "user_delete"}),
    #     name="delete_user",
    # ),
    path('api/users_delete/', UsersDelete.as_view(), name='users_delete'),
    path('api/degree_list/', DegreeList.as_view(), name='degree_list'),
    path('api/countries_list/', CountriesList.as_view(), name='countries_list'),
]
