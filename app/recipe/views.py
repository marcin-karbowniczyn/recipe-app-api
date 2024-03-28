""" Views for the recipe API """
from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe, Tag
from recipe import serializers


class RecipeViewSet(viewsets.ModelViewSet):
    """ View for manage recipe API """
    # serializer_class = serializers.RecipeSerializer  # We use get_serializer_class instead
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]  # It supports Token Authentication
    # Note: I can change it later to IsAuthenticatedOrReadOnly to allow anon users to acces GET methods.
    permission_classes = [IsAuthenticated]  # Not only that, user needs to be authenticated

    # We specify this, to limit the queryset to only recipes of the authenticated user
    def get_queryset(self):
        """ Retrieve recipes for authenticated user """
        return self.queryset.filter(user=self.request.user).order_by('-id')

    # Instead of having serializer = RecipeSerializer, we base our serializer on the action that viewset is handling
    def get_serializer_class(self):
        """ Return the serializer class for detail request """
        if self.action == 'list':
            return serializers.RecipeSerializer
        return serializers.RecipeDetailSerializer

    # We need to add this, so Django can add user to the Recipe model's user foreign key field.
    # We need to add user manually, since it's not in the req.data, and it's not processed by the serializer.
    # request.user will be set by Token Authentication
    # Serializer will be the validated serializer
    def perform_create(self, serializer):
        """ Create a new recipe """
        serializer.save(user=self.request.user)


# We should always define mixins before vewsets.GenericViewSet (DRF docs)
class TagViewSet(mixins.ListModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """ Manage tags in the databse """
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """ Filter queryset to authenticated user """
        # It can be either user_id=self.request.user.id or user=self.request.user
        return self.queryset.filter(user_id=self.request.user.id).order_by('-name')

# class TagViewSet(viewsets.ModelViewSet):
#     """ View for manage Tag API"""
#     serializer_class = serializers.TagSerializer
#     queryset = Tag.objects.all()
#     authentication_classes = [TokenAuthentication]
#     permission_classes = [IsAuthenticated]
#
#     def get_queryset(self):
#         """ Filter queryset to authenticated user """
#         # It can be either user_id=self.request.user.id or user=self.request.user
#         return self.queryset.filter(user_id=self.request.user.id).order_by('-name')
