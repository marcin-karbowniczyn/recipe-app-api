""" Views for the recipe API """
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter, OpenApiTypes
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe, Tag, Ingredient
from recipe import serializers


class RecipeViewSet(viewsets.ModelViewSet):
    """ View for manage recipe API """
    # serializer_class = serializers.RecipeSerializer  # We use get_serializer_class instead
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]  # It supports Token Authentication
    # Note: I can change it later to IsAuthenticatedOrReadOnly to allow anon users to acces GET methods.
    permission_classes = [IsAuthenticated]  # Not only that, user needs to be authenticated

    def _params_to_ints(self, query_string):
        """ Convert a list of strings to integers """
        # '1,2,3' -> [1,2,3]
        return [int(str_id) for str_id in query_string.split(',')]

    # We specify this, to limit the queryset to only recipes of the authenticated user
    def get_queryset(self):
        """ Retrieve recipes for authenticated user """
        tags = self.request.query_params.get('tags')  # This will return None if there is no tags
        ingredients = self.request.query_params.get('ingredients')
        queryset = self.queryset

        if tags:
            tag_ids = self._params_to_ints(tags)
            queryset = queryset.filter(tags__id__in=tag_ids)

        if ingredients:
            ingredient_ids = self._params_to_ints(ingredients)
            queryset = queryset.filter(ingredients__id__in=ingredient_ids)

        return queryset.filter(user=self.request.user).order_by('-id').distinct()

    # Instead of having serializer = RecipeSerializer, we base our serializer on the action that viewset is handling
    def get_serializer_class(self):
        """ Return the serializer class for detail request """
        if self.action == 'list':
            return serializers.RecipeSerializer
        elif self.action == 'upload_image':
            return serializers.RecipeImageSerializer

        return serializers.RecipeDetailSerializer

    # We need to add this, so Django can add user to the Recipe model's user foreign key field.
    # We need to add user manually, since it's not in the req.data, and it's not processed by the serializer.
    # request.user will be set by Token Authentication
    # Serializer will be the validated serializer
    def perform_create(self, serializer):
        """ Create a new recipe """
        serializer.save(user=self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """ Upload an image to recipe """
        recipe = self.get_object()
        serializer = self.get_serializer(recipe, data=request.data)  # I need to pass in recipe to fulfill validation rules

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BaseRecipeAttrViewset(mixins.ListModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]  # You cannot make a request to this endpoint, unless you are authenticated

    def get_queryset(self):
        """ Filter queryset to authenticated user """
        # It can be either user_id=self.request.user.id or user=self.request.user
        return self.queryset.filter(user_id=self.request.user.id).order_by('-name')


# We should always define mixins before vewsets.GenericViewSet (DRF docs)
class TagViewSet(BaseRecipeAttrViewset):
    """ Manage tags in the databse """
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()


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


class IngredientViewset(BaseRecipeAttrViewset):
    """ Manage ingredients in the database """
    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()

# # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! TESTING VIEWS !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# class DeleteAllView(APIView):
#     authentication_classes = [TokenAuthentication]
#     permission_classes = [IsAdminUser]
#
#     def delete(self, request, pk=None):
#         Recipe.objects.all().delete()
#         return Response({'status': 'Success', 'message': 'All recipes has beed deleted'})
