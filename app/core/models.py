""" Database models """
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """ Create, save and return a new user """

        # 1. Create user and normalize the email (set the domain part to lowercase)
        user = self.model(email=self.normalize_email(email), **extra_fields)

        # 2. Hash the password
        user.set_password(password)

        # 3. Save and return the user
        user.save(using=self._db)  # We set the "using" parameter to support adding multiple DB's.
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """ User in the project """
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
