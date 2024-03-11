""" Database models """
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """ Create, save and return a new user """
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        # We set the "using" parameter to support adding multiple DB's.

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """ User in the project """
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
