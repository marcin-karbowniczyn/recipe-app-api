""" Tests for the tags API """
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag, Recipe
from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')


def detail_url(tag_id):
    """ Create and return a URL for detailed object """
    return reverse('recipe:tag-detail', args=[tag_id])


def create_user(email='user@example.com', password='test1234'):
    """ Create and return a user """
    return get_user_model().objects.create_user(email, password)


class PublicTagsAPITests(TestCase):
    """ Test unauthenticated API requests """

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """ Test auth is required for recieving tags """
        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsAPITests(TestCase):
    """ Test authenticated API requests """

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """ Test retrieving a list of tags"""
        Tag.objects.create(name='Vegan', user=self.user)
        Tag.objects.create(name='Dessert', user=self.user)

        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Different versions of Postgres can return differernt order of object, so we want to omit this issue with .order_by('-name')
        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """ Test list of tags is limited to authenticated user """
        user2 = create_user(email='user2@example.com', password='Test1234')
        Tag.objects.create(user=user2, name='Fruity')
        tag = Tag.objects.create(user=self.user, name='Comfort Food')

        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)
        self.assertEqual(res.data[0]['id'], tag.id)

    def test_update_tag(self):
        """ Test updating a tag """
        payload = {
            'name': 'Pasta'
        }
        tag = Tag.objects.create(user=self.user, name='Vegan')
        res = self.client.patch(detail_url(tag.id), payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        tag.refresh_from_db()
        self.assertEqual(tag.name, payload['name'])

    def test_delete_tag(self):
        """ Test deleting a tag """
        tag = Tag.objects.create(user=self.user, name='Breakfast')
        res = self.client.delete(detail_url(tag.id))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        tags = Tag.objects.filter(user=self.user)
        self.assertFalse(tags.exists())

    def test_filter_tags_assigned_to_recipes(self):
        """ Test listing tags to those that are assigned to recipes """
        tag1 = Tag.objects.create(user=self.user, name='Vegetarian')
        tag2 = Tag.objects.create(user=self.user, name='Meat')

        recipe = Recipe.objects.create(
            title='Tomato Salad',
            time_minutes=10,
            price=Decimal('1.50'),
            user=self.user,
        )
        recipe.tags.add(tag1)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        serialized_tag1 = TagSerializer(tag1)
        serialized_tag2 = TagSerializer(tag2)

        self.assertIn(serialized_tag1.data, res.data)
        self.assertNotIn(serialized_tag2.data, res.data)

    def test_filtered_tags_unique(self):
        tag1 = Tag.objects.create(user=self.user, name='Breakfast')
        Tag.objects.create(user=self.user, name='Dinner')

        recipe1 = Recipe.objects.create(
            title='Scrumbled Eggs',
            time_minutes=10,
            price=Decimal('1.00'),
            user=self.user,
        )

        recipe2 = Recipe.objects.create(
            title='Croque Madam',
            time_minutes=20,
            price=3.00,
            user=self.user,
        )
        recipe1.tags.add(tag1)
        recipe2.tags.add(tag1)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})
        self.assertEqual(len(res.data), 1)
