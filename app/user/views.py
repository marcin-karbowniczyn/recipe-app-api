""" Views for the User API """
from rest_framework import generics
from .serializers import UserSerializer


# CreateAPIView is used for create-only endpoints.
class CreateUserView(generics.CreateAPIView):
    """ Create a new user in the system """
    serializer_class = UserSerializer
