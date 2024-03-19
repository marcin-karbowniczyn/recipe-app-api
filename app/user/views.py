""" Views for the User API """
from django.contrib.auth import get_user_model
from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from .serializers import UserSerializer, AuthTokenSerializer
from .permissions import IsSuperUser


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
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES  # optional


# RetrieveUpdateAPIView is a DRF Api View for getting and updating API objects
class ManageUserView(generics.RetrieveUpdateAPIView):
    """ Manage the authenticated user """
    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    # Vid. 72
    def get_object(self):
        """ Retrieve and return the authenticated user """
        # When the user is autehnticated, it will be accesible from request.user
        # get() executes retrieve() -> retrieve uses get_object() and sends a response
        return self.request.user


class GetAllUsersView(generics.ListAPIView):
    """ Admin's Get All Users (Only for testing) """
    serializer_class = UserSerializer
    queryset = get_user_model().objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsSuperUser]
