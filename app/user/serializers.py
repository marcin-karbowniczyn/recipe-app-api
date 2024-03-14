""" Serializers for the user API view """
from django.contrib.auth import get_user_model
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """ Serializer for the user object """

    class Meta:
        model = get_user_model()
        fields = ['email', 'password', 'name']
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    # Remainder: this method by default simply calls the create() method of the manager we specified in Meta's model.
    # We want to override it, because the default method wouldn't hash the password.
    # This method will be called only if the validation was successful
    def create(self, validated_data):
        """ Create and return a user with encrypted password """
        return get_user_model().objects.create_user(**validated_data)
