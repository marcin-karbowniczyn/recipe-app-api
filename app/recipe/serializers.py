""" Serializers for recipe API """
from rest_framework import serializers
from core.models import Recipe, Tag, Ingredient


class IngredientSerializer(serializers.ModelSerializer):
    """ Serializer for Ingredients """

    class Meta:
        model = Ingredient
        fields = ['id', 'name']
        read_only_fields = ['id']


class TagSerializer(serializers.ModelSerializer):
    """ Serializer for Tags """

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']  # Optional, id is read-only by default


class RecipeSerializer(serializers.ModelSerializer):
    """ Serializer for Recipes """
    tags = TagSerializer(many=True, required=False)
    ingredients = IngredientSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'time_minutes', 'price', 'link', 'tags', 'ingredients']
        # extra_kwargs = {'user': {'read_only': True}} # If allowed, remember to add 'user' to the fields

    # Enabling user to be sent in a response as a name of the user, not id of the user
    # def to_representation(self, instance):
    #     response = super().to_representation(instance)
    #     response['user'] = instance.user.name
    #     return response

    def _get_or_create_tags(self, tags, recipe):
        """ Handle getting or creating tags """
        authenticated_user = self.context['request'].user
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(user=authenticated_user, **tag)
            recipe.tags.add(tag_obj)

    # We need to specify custom create() and update() methods because nested fields are read-only by default.
    # We need to override them methods for the creating and updating many-to-many fields to work.
    def create(self, validated_data):
        """ Create a recipe """
        # 1. Remove tags from validated data and return them
        tags = validated_data.pop('tags', [])

        # 2. Create a new recipe object with correct values
        recipe = Recipe.objects.create(**validated_data)

        # 3. Get authenticated user from the request and loop through tags from validated data
        self._get_or_create_tags(tags, recipe)

        return recipe

    def update(self, instance, validated_data):
        """ Update a recipe """
        tags = validated_data.pop('tags', None)
        # If empty array, it will enter the if block and clear all the tags from the recipe
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)  # Instance = recipe

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class RecipeDetailSerializer(RecipeSerializer):
    """ Serializer for Recipe Detail View """

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']
