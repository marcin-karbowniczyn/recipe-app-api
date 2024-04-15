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
        """ Handle getting or creating tags and ingredients """
        authenticated_user = self.context['request'].user
        for tag in tags:
            tag['name'] = ' '.join(tag['name'].split()).title()
            tag_obj, created = Tag.objects.get_or_create(user=authenticated_user, **tag)
            recipe.tags.add(tag_obj)

    def _get_or_create_ingredients(self, ingredients, recipe):
        """ Handle getting or creating ingredients """
        authenticated_user = self.context['request'].user
        for ingredient in ingredients:
            # This makes sure that we won't have repetetive ingredients in the DB.
            ingredient['name'] = ' '.join(ingredient['name'].split()).title()
            ingredient_obj, created = Ingredient.objects.get_or_create(user=authenticated_user, **ingredient)
            recipe.ingredients.add(ingredient_obj)

    # We need to specify custom create() and update() methods because nested M2M fields are read-only by default.
    # We need to override these methods for creating and updating many-to-many fields to work.
    # validated_data is a python dictionary of all the data passed in the request
    # By default create() and update() methods in serializer simply call Manager's create and update methods (reminder)
    def create(self, validated_data):
        """ Create a recipe """
        # 1. Remove tags and ingredients from validated data and return them
        tags = validated_data.pop('tags', [])
        ingredients = validated_data.pop('ingredients', [])

        # 2. Create a new recipe object with correct values
        recipe = Recipe.objects.create(**validated_data)

        # 3. Get authenticated user from the request and loop through tags and ingredients from validated data
        self._get_or_create_tags(tags, recipe)
        self._get_or_create_ingredients(ingredients, recipe)

        return recipe

    def update(self, instance, validated_data):
        """ Update a recipe """
        tags = validated_data.pop('tags', None)
        ingredients = validated_data.pop('ingredients', None)
        # If empty array, it will enter the if block and clear all the tags from the recipe
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)  # Instance = recipe

        if ingredients is not None:
            instance.ingredients.clear()
            self._get_or_create_ingredients(ingredients, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class RecipeDetailSerializer(RecipeSerializer):
    """ Serializer for Recipe Detail View """

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']
