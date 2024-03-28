""" Serializers for recipe API """
from rest_framework import serializers
from core.models import Recipe, Tag


class RecipeSerializer(serializers.ModelSerializer):
    """ Serializer for Recipes """

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'time_minutes', 'price', 'link']
        # extra_kwargs = {'user': {'read_only': True}} # If allowed, remember to add 'user' to the fields

    # Enabling user to be sent in a response as a name of the user, not id of the user
    # def to_representation(self, instance):
    #     response = super().to_representation(instance)
    #     response['user'] = instance.user.name
    #     return response


class RecipeDetailSerializer(RecipeSerializer):
    """ Serializer for Recipe Detail View """

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']


class TagSerializer(serializers.ModelSerializer):
    """ Serializer for Tags """

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']  # Optional, id is read-only by default
