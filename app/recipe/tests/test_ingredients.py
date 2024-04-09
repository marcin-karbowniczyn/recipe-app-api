""" Tests for ingredients API """
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient  # CHANgE IT TO from core.models import Ingredient AFTER TESTING !!!!!!!!!!!!!!!!!
from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse('recipe:ingredient-list')


def detail_url(ingredient_id):
    """ Create a URL for a detailed object """
    return reverse('recipe:ingredient-detail', args=[ingredient_id])


def create_user(email='user@example.com', password='test1234'):
    """ Create and return a user """
    return get_user_model().objects.create_user(email, password)


class PublicIngredientsAPITests(TestCase):
    """ Test unaithenticated API requests """

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """ Test auth is reqiored for retrieving ingredients """
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsAPITests(TestCase):
    """ Test authenticated API requests """

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieving_ingredients(self):
        Ingredient.objects.create(user=self.user, name='Salt')
        Ingredient.objects.create(user=self.user, name='Pepper')

        res = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.all().order_by('name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        # self.assertEqual(ingredients.values(), serializer.data) # Sprawdzić czy działa

    def test_ingredients_limited_to_user(self):
        """ Test retrieved ingredients are limited to user that created them """
        ingredient = Ingredient.objects.create(user=self.user, name='Paprika')

        new_user = create_user('user2@example.com', password='test1234')
        Ingredient.objects.create(user=new_user, name='Cabbage')

        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertEqual(len(res.data), 1)
        self.assertEqual(ingredient.name, res.data[0]['name'])
        self.assertEqual(ingredient.id, res.data[0]['id'])

    def test_update_ingredient(self):
        """ Test updating an ingredient """
        ingredient = Ingredient.objects.create(user=self.user, name='Pepper')
        payload = {'name': 'Salt'}

        res = self.client.patch(detail_url(ingredient.id), payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        ingredient.refresh_from_db()
        self.assertEqual(ingredient.name, payload['name'])
