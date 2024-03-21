""" Views for the recipe API """
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe
from recipe import serializers


class RecipeViewSet(viewsets.ModelViewSet):
    """ View for manage recipe API """
    serializer_class = serializers.RecipeSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]  # It supports Token Authentication
    permission_classes = [IsAuthenticated]  # Not only that, user needs to be authenticated

    # We specify this, to limit the queryset to only recipes of the authenticated user
    def get_queryset(self):
        """ Retrieve recipes for authenticated user """
        return self.queryset.filter(user=self.request.user).order_by('-id')
