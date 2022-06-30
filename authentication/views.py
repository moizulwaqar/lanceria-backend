from django.shortcuts import redirect, render
from django.utils.encoding import force_bytes, force_text
from django.db import transaction
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.tokens import RefreshToken

from user_profile.serializers import UpdateProfileSerializer
from .models import User, UserProfile
from .serializers import SignUpCheckEmailSerializer, EmailSignUpSerializer, SocialAuthSerializer, \
    LoginCheckEmailSerializer, EmailLoginSerializer, GenerateUserName, RoleChangeSerializer, ForgotPasswordSerializer, \
    ResetPasswordSerializer, EmailSignUpValidationSerializer, LogoutSerializer, \
    FreelancerViewSerializer, EmployerViewSerializer
from django.db.models import Q
from rest_framework.views import APIView
from lanceria_backend.utils import Util
from authentication.tokens import account_activation_token
from lanceria_backend.settings import PANEL_BASE_URL, Base_URL, Redirect_Url
from uuid import uuid4

# Create your views here.


def user_name(first_name, last_name):
    # n = random.randint(0, 999999)
    # # full_name = first_name + last_name
    # full_name = "{0}{1}".format(first_name, last_name[0]).lower()
    # username = full_name + str(n)
    # return username
    # val = "{0}{1}{2}".format("@", first_name, last_name).lower()
    val = "{0}{1}".format(first_name, last_name).lower()
    x = 0
    while True:
        if x == 0 and User.objects.filter(username=val).count() == 0:
            return val
        else:
            new_val = "{0}{1}{2}".format(val, "_", x)
            if User.objects.filter(username=new_val).count() == 0:
                return new_val
        x += 1
        if x > 10000000:
            raise Exception("Name is super popular!")


def password_check(param):
    pass


class UserViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    @staticmethod
    def signup_check_email(request):
        serializer = SignUpCheckEmailSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                     "errors": e.args[0]}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        response = {"statusCode": 200, "error": False, "data": serializer.data,
                    "message": "User with this email not exist!"}
        return Response(response, status=status.HTTP_200_OK)

    def create(self, request):
        serializer = EmailSignUpValidationSerializer(data=request.data, context={"request": request})
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                     "errors": e.args[0]}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        serializer = EmailSignUpSerializer(data=request.data, context={"request": request})
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                     "errors": e.args[0]}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        password = make_password(self.request.data['password'])
        email = serializer.validated_data['email']
        serializer.save(password=password, email=email.lower())
        user = User.objects.filter(email=email.lower()).first()
        euuid = str(uuid4())
        fuuid = str(uuid4())
        user.e_uuid = euuid
        user.f_uuid = fuuid
        user.save()
        link = Base_URL + urlsafe_base64_encode(
            force_bytes(user.pk)) + '/' + account_activation_token.make_token(
            user) + '/'
        Util.sendEmailTemplate({
            'subject': 'Email Verification Link',
            'template': 'email_templates/email_verification.html',
            'receiver_email': request.data['email'],
            'templateObject': {
                'link': link
            }
        })
        user = User.objects.get(email=email.lower())
        freelancer_profile = UserProfile()
        freelancer_profile.user = user
        freelancer_profile.title = ""
        freelancer_profile.description = ""
        freelancer_profile.role = "Freelancer"
        freelancer_profile.save()
        employer_profile = UserProfile()
        employer_profile.user = user
        employer_profile.title = ""
        employer_profile.description = ""
        employer_profile.role = "Employer"
        employer_profile.save()
        refresh = RefreshToken.for_user(user)
        data = {
            "token": str(refresh.access_token),
            "refresh_token": str(refresh),
            "user": EmailSignUpSerializer(user).data
        }
        response = {"statusCode": 201, "error": False, "data": data,
                    "message": "Successfully SignUp and Sent Email for Verification!"}
        return Response(response, status=status.HTTP_201_CREATED)

    @staticmethod
    def login_check_email(request):
        serializer = LoginCheckEmailSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                     "errors": e.args[0]}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        response = {"statusCode": 200, "error": False, "data": serializer.data,
                    "message": "User with this email exist!"}
        return Response(response, status=status.HTTP_200_OK)

    @staticmethod
    def email_login(request):
        serializer = EmailLoginSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            message = {"email": [""], "password": [e.args[0]]}
            error = {"statusCode": 400, "error": True, "data": "", "message": "Invalid credentials, try again",
                     "errors": message}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.get(email=request.data['email'])
        refresh = RefreshToken.for_user(user)
        data = {
            "token": str(refresh.access_token),
            "refresh_token": str(refresh),
            "user": serializer.data
        }
        response = {"statusCode": 200, "error": False, "data": data, "message": "User successfully Login!"}
        return Response(response, status=status.HTTP_200_OK)

    def generate_username(self, request):
        serializer = GenerateUserName(data=self.request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                     "errors": e.args[0]}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        while True:
            username = user_name(request.data.get("first_name"), request.data.get("last_name"))
            if not User.objects.filter(username=username).exists():
                break
        response = {"statusCode": 200, "error": False, "data": username, "message": "Username successfully generated!"}
        return Response(response, status=status.HTTP_200_OK)

    def social_login(self, request):
        serializer = SocialAuthSerializer(data=self.request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                     "errors": e.args[0]}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.get(Q(email=self.request.data.get("email")) |
                                Q(provider_id=self.request.data.get("provider_id")))
        data = {
            'refresh': user.tokens()['refresh'],
            'access': user.tokens()['access'],
            'id': user.id,
            'email': user.email,
            'provider': user.provider,
            'provider_id': user.provider_id,
        }
        response = {"statusCode": 200, "error": False, "data": data, "message": "Successfully Login!"}
        return Response(response, status=status.HTTP_200_OK)

    @staticmethod
    def forgot_password(request):
        try:
            serializer = ForgotPasswordSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            with transaction.atomic():
                user = User.objects.filter(email=request.data['email']).first()
                link = PANEL_BASE_URL + urlsafe_base64_encode(
                    force_bytes(user.pk)) + '/' + account_activation_token.make_token(
                    user) + '/'
                Util.sendEmailTemplate({
                    'subject': 'Reset Password Link',
                    'template': 'email_templates/forget_password.html',
                    'receiver_email': request.data['email'],
                    'templateObject': {
                        'link': link
                    }
                })
                response = {"statusCode": 200, "error": False, "message": "Email for Password Reset sent successfully!"}
                return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                     "errors": e.args[0]}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def reset_password(request, uidb64, token):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64.strip()))
            if not User.objects.filter(id=uid).exists():
                message = {"message": {"User does not exist!"}}
                error = {"statusCode": 404, "error": True, "data": "", "message": "User does not exist",
                         "errors": message}
                return Response(error, status=status.HTTP_404_NOT_FOUND)
            user = User.objects.get(pk=uid)
        except():
            user = None
        if user is not None and account_activation_token.check_token(user, token):
            serializer = ResetPasswordSerializer(data=request.data)
            try:
                serializer.is_valid(raise_exception=True)
            except Exception as e:
                error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                         "errors": e.args[0]}
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
            if user.check_password(request.data['password']):
                message = {"message": {"You cannot use an old password!"}}
                response = {"statusCode": 400, "error": True, "data": "",
                            "message": "You cannot use an old password!", "errors": message}
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(str(request.data['password']))
            user.save()
            response = {"statusCode": 200, "error": False, "message": "Password Reset successfully!"}
            return Response(response, status=status.HTTP_200_OK)
        else:
            message = {"message": {"Link has been expired!"}}
            response = {"statusCode": 404, "error": True, "data": "",
                        "message": "Link has been expired!", "errors": message}
            return Response(response, status=status.HTTP_404_NOT_FOUND)

    @staticmethod
    def email_verification(request, uidb64, token):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64.strip()))
            user = User.objects.get(pk=uid)
            if user.email_verified:
                return render(request, "email_templates/email_verified.html")
        except():
            user = None
        if user is not None and account_activation_token.check_token(user, token):
            user.email_verified = True
            user.save()
            return redirect(Redirect_Url)
        else:
            return render(request, "email_templates/expire_link.html")

    @staticmethod
    def logout(request):
        try:
            serializer = LogoutSerializer(data=request.data)
            try:
                serializer.is_valid(raise_exception=True)
            except Exception as e:
                error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                         "errors": e.args[0]}
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
            refresh_token = request.data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()
            error = {"statusCode": 200, "error": False, "message": "Logout successfully!"}
            return Response(error)
        except:
            message = {"message": {"Invalid token"}}
            error = {"statusCode": 404, "error": True, "data": "", "message": "Bad Request, Please check request",
                     "errors": message}
            return Response(error, status=status.HTTP_404_NOT_FOUND)

    @staticmethod
    def public_view(request, token):
        try:
            if User.objects.filter(f_uuid=token).exists():
                user = User.objects.filter(f_uuid__iexact=token).first()
                serializer = FreelancerViewSerializer(user, many=False)
                profile_serializer = UpdateProfileSerializer(UserProfile.objects.filter(user=user,
                                                                                        role="Freelancer").first()).data
                data = {
                    "user": dict(serializer.data, **profile_serializer)
                }
                error = {"statusCode": 200, "error": False, "data": data, "message": "Freelancer Details!"}
                return Response(error)
            elif User.objects.filter(e_uuid=token).exists():
                user = User.objects.filter(e_uuid__iexact=token).first()
                serializer = EmployerViewSerializer(user, many=False)
                profile_serializer = UpdateProfileSerializer(UserProfile.objects.filter(user=user,
                                                                                        role="Employer").first()).data
                data = {
                    "user": dict(serializer.data, **profile_serializer)
                }
                error = {"statusCode": 200, "error": False, "data": data, "message": "Employer Details!"}
                return Response(error)
            else:
                message = {"message": {"Invalid Address"}}
                error = {"statusCode": 401, "error": True, "data": "", "message": "Bad Request, Please check request",
                         "errors": message}
                return Response(error, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            error = {"success": False, "message": e.args[0], "data": ""}
            return Response(error)

    @staticmethod
    def resend_verfication(request):
        try:
            user = request.user
            if user.email:
                if not user.email_verified:
                    link = Base_URL + urlsafe_base64_encode(
                        force_bytes(user.pk)) + '/' + account_activation_token.make_token(
                        user) + '/'
                    Util.sendEmailTemplate({
                        'subject': 'Email Verification Link',
                        'template': 'email_templates/email_verification.html',
                        'receiver_email': user.email,
                        'templateObject': {
                            'link': link
                        }
                    })
                    response = {"statusCode": 200, "error": False,
                                "message": "Successfully Sent Email for Verification!"}
                    return Response(response, status=status.HTTP_200_OK)
                else:
                    message = {"message": {"Your Email Already Verified!"}}
                    error = {"statusCode": 403, "error": True, "data": "",
                             "message": "Your Email Already Verified!", "errors": message}
                    return Response(error, status=status.HTTP_403_FORBIDDEN)
            else:
                message = {"message": {"Email does not exist!"}}
                error = {"statusCode": 404, "error": True, "data": "",
                         "message": "Bad Request, Please check request", "errors": message}
                return Response(error, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                     "errors": e.args[0]}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

    def get_permissions(self):
        if self.action in ["logout"] or self.action in ['resend_verfication']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]


class ChangeRole(APIView):
    permission_classes = (IsAuthenticated,)

    @staticmethod
    def post(request):
        serializer = RoleChangeSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                     "errors": e.args[0]}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        user = request.user
        user.role = request.data.get("role")
        user.save()
        data = {"id": user.id, "role": request.data.get("role")}
        response = {"statusCode": 200, "error": False, "data": data, "message": "Role Successfully Changed!"}
        return Response(response, status=status.HTTP_200_OK)
