from django.urls import path, include
from rest_framework_simplejwt import views as jwt_views
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, ChangeRole
router = DefaultRouter()

urlpatterns = [

    path(
        "api/signup_check_email",
        UserViewSet.as_view({"post": "signup_check_email"}),
        name="check_email",
    ),
    path(
        "api/email_signup",
        UserViewSet.as_view({"post": "create"}),
        name="create",
    ),
    path(
        "api/login_check_email",
        UserViewSet.as_view({"post": "login_check_email"}),
        name="check_email",
    ),
    path(
        "api/email_login",
        UserViewSet.as_view({"post": "email_login"}),
        name="check_email",
    ),
    # Generate Username for social signup
    path(
        "api/generate_username",
        UserViewSet.as_view({"post": "generate_username"}),
        name="generate_username",
    ),
    # Social Login/Signup Google, Facebook and Apple
    path(
        "api/social_login",
        UserViewSet.as_view({"post": "social_login"}),
        name="social_login",
    ),
    path(
        "api/change_role",
        ChangeRole.as_view(),
        name="change_role",
    ),
    path(
        "api/forgot_password",
        UserViewSet.as_view({"post": "forgot_password"}),
        name="forgot_password",
    ),
    path(
        "api/reset_password/<uidb64>/<token>/",
        UserViewSet.as_view({"post": "reset_password"}),
        name="reset_password",
    ),
    path(
        "api/email_verification/<uidb64>/<token>/",
        UserViewSet.as_view({"get": "email_verification"}),
        name="email_verification",
    ),
    path(
        "api/logout",
        UserViewSet.as_view({"post": "logout"}),
        name="logout",
    ),
    path(
        "api/public_view/<token>/",
        UserViewSet.as_view({"get": "public_view"}),
        name="public_view",
    ),
    path(
        "api/resend_verfication",
        UserViewSet.as_view({"get": "resend_verfication"}),
        name="resend_verfication",
    ),
    path('api/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path("", include(router.urls)),
]
