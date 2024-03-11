""" Tests for models """
from django.test import TestCase
from django.contrib.auth import get_user_model  # helper function to get a default user model for the project


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
