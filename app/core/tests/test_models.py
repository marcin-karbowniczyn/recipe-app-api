""" Tests for models """
from decimal import Decimal
from unittest.mock import patch
from django.test import TestCase
from django.contrib.auth import get_user_model  # helper function to get a default user model for the project
from .. import models


def create_user(email='user@example.com', password='testpass1234'):
    """ Create and return a new user """
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):
    """ Test models """

    def test_create_user_with_email_succesful(self):
        """ Test if creating a user with an email is successful """
        email = 'test@example.com'
        password = 'testpass1234'
        user = get_user_model().objects.create_user(email=email, password=password)

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
        # Password is saved as a hashed password, so we need to use this function which is provided by the default user model manager (Base User Manager)

    def test_new_user_email_normalized(self):
        """ Test if email is normalized for new users """
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com']
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'sample123')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """ Test that creating a user without an email raises a ValueError """
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'test123')

    def test_create_superuser(self):
        """ Test creating a superuser """
        user = get_user_model().objects.create_superuser('test@example.com', 'test123')

        self.assertTrue(user.is_superuser)  # is_superuser is a field provided by the PermissionsMixin
        self.assertTrue(user.is_staff)

    def test_create_recipe(self):
        """ Test creating a recipe is successful """
        user = get_user_model().objects.create_user(email='test@example.com', password='testpass1234')
        recipe = models.Recipe.objects.create(
            user=user,
            title='Sample Recipe Name',
            time_minutes=5,
            price=Decimal('5.50'),
            description='Test Description.'
        )

        self.assertEqual(str(recipe), recipe.title)

    def test_create_tag(self):
        """ Test creating a tag is successful """
        user = create_user()
        tag = models.Tag.objects.create(user=user, name='Tag1')

        self.assertEqual(str(tag), tag.name)

    def test_create_ingredient(self):
        """ Test creating an ingredient is succesful """
        user = create_user()
        ingredient = models.Ingredient.objects.create(user=user, name='Ingredient1')

        self.assertEqual(str(ingredient), ingredient.name)

    @patch('core.models.uuid.uuid4')  # uuid generates a random string (unique identifier)
    def test_recipe_file_name_uuid(self, mock_uuid):
        """ Test generating image path """
        uuid = 'test_uuid'
        mock_uuid.return_value = uuid
        file_patch = models.recipe_image_file_path(None, 'example.jpg')

        self.assertEqual(file_patch, f'uploads/recipe/{uuid}.jpg')
