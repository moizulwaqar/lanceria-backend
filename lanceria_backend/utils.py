from django.http import Http404
from rest_framework import exceptions
import threading
from django.core.mail import EmailMessage, send_mail
from django.template.loader import render_to_string
from rest_framework.views import exception_handler
from rest_framework.exceptions import NotAuthenticated, AuthenticationFailed, PermissionDenied, NotFound, \
    MethodNotAllowed, NotAcceptable, UnsupportedMediaType, ValidationError
from rest_framework.response import Response
from rest_framework import status


class PermissionsUtil:

    @staticmethod
    def permission(request, instance):
        if request.user.is_superuser or instance.user == request.user:
            return True
        raise exceptions.PermissionDenied()


class EmailThread(threading.Thread):

    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()


class EmailThreading(threading.Thread):
    def __init__(self, data):
        self.data = data
        threading.Thread.__init__(self)

    def run(self):
        template = render_to_string(self.data['template'], self.data['templateObject'])
        send_mail(subject=self.data['subject'], message=template, html_message=template,
                  from_email='tmailspyresync@gmail.com', recipient_list=[self.data['receiver_email']])


class Util:
    @staticmethod
    def send_email(data):
        email1 = EmailMessage(
            subject=data['email_subject'], body=data['email_body'], to=[data['to_email']])
        EmailThread(email1).start()

    @staticmethod
    def sendEmailTemplate(data):
        EmailThreading(data).start()
        # template = render_to_string(data['template'], data['templateObject'])
        # send_mail(subject=data['subject'], message=template, html_message=template,
        #           from_email='tmailspyresync@gmail.com', recipient_list=[data['receiver_email']])


def custom_exception_handler(exc, context):
    if isinstance(exc, NotAuthenticated):
        message = {"messages": [exc.detail]}
        return Response({"statusCode": 401, "error": True, "data": "", "message": exc.detail, "errors": message},
                        status=401)
    if isinstance(exc, AuthenticationFailed):
        # message = {"messages": exc.detail.get('messages')}
        message = {"messages": exc.detail.get('detail')}
        return Response({"statusCode": 401, "error": True, "data": "", "message": exc.detail.get('detail'),
                         "errors": message}, status=401)
    if isinstance(exc, PermissionDenied):
        message = {"messages": exc.detail}
        return Response({"statusCode": 403, "error": True, "data": "", "message": exc.detail,
                         "errors": message}, status=403)
    if isinstance(exc, NotFound):
        message = {"messages": exc.detail}
        return Response({"statusCode": 404, "error": True, "data": "", "message": exc.detail,
                         "errors": message}, status=404)
    if isinstance(exc, MethodNotAllowed):
        message = {"messages": exc.detail}
        return Response({"statusCode": 405, "error": True, "data": "", "message": exc.detail,
                         "errors": message}, status=405)
    if isinstance(exc, NotAcceptable):
        message = {"messages": exc.detail}
        return Response({"statusCode": 406, "error": True, "data": "", "message": exc.detail,
                         "errors": message}, status=406)
    if isinstance(exc, UnsupportedMediaType):
        message = {"messages": exc.detail}
        return Response({"statusCode": 415, "error": True, "data": "", "message": exc.detail,
                         "errors": message}, status=415)
    if isinstance(exc, Http404):
        message = {"messages": [exc.args[0]]}
        return Response({"statusCode": 404, "error": True, "data": "", "message": exc.args[0],
                         "errors": message}, status=404)
    if isinstance(exc, ValidationError):
        return Response(exc.args[0], status=400)
    return exception_handler(exc, context)


class Responses:
    @staticmethod
    def error_response(status_code, error, data, message, errors):
        error = {"statusCode": status_code, "error": error, "data": data, "message": message,
                 "errors": errors}
        return Response(error, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def success_response(status_code, error, data, message, response_status):
        response = {"statusCode": status_code, "error": error, "data": data,
                    "message": message}
        return Response(response, status=response_status)
