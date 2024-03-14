""" Tests for the user API """
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse  # reverse function allows us to get the URL from the name of the view that we want to get the URL for

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')


def create_user(**kwargs):
    """ Create and return a new user """
    return get_user_model().objects.create_user(**kwargs)


# The database is cleared before each test, so the user doesn't exist before that specific test.
class PublicUserAPITests(TestCase):
    """ Test the public features of the user API """

    def setUp(self):
        self.client = APIClient()

    def test_create_user_sucess(self):
        """ Test if creating a user is successful """
        payload = {
            'email': 'test@example.com',
            'password': 'testpass1234',
            'name': 'Test Name',
        }

        # 1. Check if statusCode was 201
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # 2. Check if user was actually created
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))

        # 3. Check if password is not inside the response (there is no key password in the response)
        self.assertNotIn('password', res.data)

    def test_user_with_email_exists_error(self):
        """ Test if error is returned if user with email exists """
        payload = {
            'email': 'test@example.com',
            'password': 'testpass1234',
            'name': 'Test Name'
        }
        # Remainder for my future self, ** unpacks the dictionary here, key-value pairs are passed as keyword arguments
        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """ Test if error is returned if password is less than 5 chars """
        payload = {
            'email': 'test@example.com',
            'password': 'pw',
            'name': 'Test Name'
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        # # exists() returns true if queryset contains any result
        user_exists = get_user_model().objects.filter(email=payload['email']).exists()
        self.assertFalse(user_exists)
