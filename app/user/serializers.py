""" Serializers for the user API view """
from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext as _
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
        user = get_user_model().objects.create_user(**validated_data)
        return user

    # The same case as in create method, we need to override update method to hash the password (by default it's not hashed)
    def update(self, instance, validated_data):
        """ Update and return user """
        # 1. If there is a password return it and remove it from validated_data, if not return None
        password = validated_data.pop('password', None)
        # 2. Use the default update class (we don't need to reinvent the wheel)
        user = super().update(instance, validated_data)
        # 3. If user wants to change his password, set it to updated user and has it.
        if password:
            user.set_password(password)
            user.save()
        # 4. Return a user
        return user


class AuthTokenSerializer(serializers.Serializer):
    """ Serializer for the user auth token """
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    # Unlike in the ModelSerializer, we need to specify validation by ourselves
    def validate(self, attrs):
        """ Validate and authenticate the user """
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(
            # We need to pass request here, it is a required field v.70
            request=self.context.get('request'),
            username=email,
            password=password
        )

        if not user:
            msg = _('Unable to authenticate with provided credentials.')
            # Standard way of raising errors with serializers, if we raise the error, view translates it into HTTP 400 bad request reponse
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs
