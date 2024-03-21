""" Serializers for recipe API """
from rest_framework import serializers
from core.models import Recipe


class RecipeSerializer(serializers.ModelSerializer):
    """ Serializer for recipes """

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'time_minutes', 'price', 'link']


class RecipeDetailSerializer(RecipeSerializer):
    """ Serializer for Recipe Detail View """

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']
