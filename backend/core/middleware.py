from django.utils.deprecation import MiddlewareMixin
from rest_framework.exceptions import AuthenticationFailed
from .services import JWTService


class JWTAuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.replace('Bearer ', '')
            user, error = JWTService.get_user_from_token(token)
            if user and not error:
                request.user = user
            else:
                request.auth_error = error