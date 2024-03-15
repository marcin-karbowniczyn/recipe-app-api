""" Views for the User API """
from rest_framework import generics
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from .serializers import UserSerializer, AuthTokenSerializer


# CreateAPIView is used for create-only endpoints.
class CreateUserView(generics.CreateAPIView):
    """ Create a new user in the system """
    serializer_class = UserSerializer


# ObtainAuthToken is a view provided by DRF for coreating Auth Tokens. It does most of the work for us.
class CreateTokenView(ObtainAuthToken):
    """ Create a new auth token for the user """
    # ObtainAuthToken View by default uses a username instead of email,
    # so we provide our custom serialzier to override this behaviour
    serializer_class = AuthTokenSerializer
    # renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES  # optional
