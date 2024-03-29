""" Serializers for recipe API """
from rest_framework import serializers
from core.models import Recipe, Tag


class TagSerializer(serializers.ModelSerializer):
    """ Serializer for Tags """

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']  # Optional, id is read-only by default


class RecipeSerializer(serializers.ModelSerializer):
    """ Serializer for Recipes """
    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'time_minutes', 'price', 'link', 'tags']
        # extra_kwargs = {'user': {'read_only': True}} # If allowed, remember to add 'user' to the fields

    # Enabling user to be sent in a response as a name of the user, not id of the user
    # def to_representation(self, instance):
    #     response = super().to_representation(instance)
    #     response['user'] = instance.user.name
    #     return response

    def create(self, validated_data):
        """ Create a recipe """
        # 1. Remove tags from validated data
        tags = validated_data.pop('tags', [])

        # 2. Create a new recipe object with correct values
        recipe = Recipe.objects.create(**validated_data)

        # 3. Get authenticated user from the request
        auth_user = self.context['request'].user

        # 4. Loop through tags from validated data
        for tag in tags:
            # get_or_create() -> Manager's helper function, it gets the object if it exists, if not it creates it.
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag,
            )
            # add() -> Adds object to many-to-many field of related object (Recipe in our case)
            recipe.tags.add(tag_obj)

        return recipe


class RecipeDetailSerializer(RecipeSerializer):
    """ Serializer for Recipe Detail View """

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']
