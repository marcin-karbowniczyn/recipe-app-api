""" Tests for recipe API """
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag
from ..serializers import RecipeSerializer, RecipeDetailSerializer

RECIPES_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    """ Create and return a URL for detailed object """
    return reverse(f'recipe:recipe-detail', args=[recipe_id])


def create_recipe(user, **kwargs):
    """ Create and return a test recipe """
    defaults = {
        'title': 'Sample recipe title',
        'time_minutes': 22,
        'price': Decimal('5.25'),
        'description': 'Test description of the recipe.',
        'link': 'http://example.com/recipe.pdf',
    }
    defaults.update(kwargs)
    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe


def create_user(**params):
    """ Create and return a new user """
    return get_user_model().objects.create_user(**params)


class PublicRecipeAPITests(TestCase):
    """ Test unauthenticated API requests """

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """ Test if auth is required to call API """
        res = self.client.get(RECIPES_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITests(TestCase):
    """ Test authenticated API requests """

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email='user@example.com', password='test1234')
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """ Test if listing recipes works for authenticated users """
        create_recipe(user=self.user)
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-id')  # '-' -> sorting in reverse order
        # To serialize a queryset or list of objects instead of a single object instance, you should pass the many=True flag when instantiating the serializer.
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipe_list_limited_to_user(self):
        """ Test list of recipes is limited to authenticated user """
        other_user = create_user(email='other@example.com', password='password1234')
        create_recipe(user=other_user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_recipe_detail(self):
        """ Test get recipe detail """
        recipe = create_recipe(user=self.user)
        res = self.client.get(detail_url(recipe.id))

        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe(self):
        """ Test creating a recipe """
        payload = {
            'title': 'Sample recipe',
            'time_minutes': 30,
            'price': Decimal('5.99'),
        }
        res = self.client.post(RECIPES_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # Remainder for me: recipe is an object not a dictionary
        recipe = Recipe.objects.get(id=res.data['id'])
        for key, value in payload.items():
            self.assertEqual(getattr(recipe, key), value)
        self.assertEqual(recipe.user, self.user)

    def test_partial_update(self):
        """ Test patching a recipe """
        original_link = 'https://example.com/recipe.pdf'
        recipe = create_recipe(user=self.user, title='Sample recipe title', link=original_link)
        payload = {'title': 'Updated sample recipe title'}

        res = self.client.patch(detail_url(recipe.id), payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.link, original_link)
        self.assertEqual(recipe.user, self.user)

    def test_full_update(self):
        """ Test full update of a recipe  """
        # 1. Create a new recipe
        recipe = create_recipe(self.user)
        # 2. Set the payload of the updated recipe
        payload = {
            'title': 'New updated test title',
            'time_minutes': 69,
            'price': Decimal('4.20'),
            'description': 'New updated description of the recipe.',
        }
        # 3. Update the recipe
        res = self.client.put(detail_url(recipe.id), payload)

        # 4. Test if status of the request is 200
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # 5. Refresh the recipe object
        recipe.refresh_from_db()

        # 6. Check if updated object is the same as payload
        for key, value in payload.items():
            self.assertEqual(getattr(recipe, key), value)
        self.assertEqual(self.user, recipe.user)

    def test_cannot_update_user_of_recipe(self):
        """ Test changing the user(creator) of the recipe doesn't work """
        new_user = create_user(email='user2@example.com', password='test1234')
        recipe = create_recipe(user=self.user)
        payload = {'user': new_user.id}
        self.client.patch(detail_url(recipe.id), payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.user, self.user)

    def test_delete_recipe(self):
        recipe = create_recipe(self.user)
        res = self.client.delete(detail_url(recipe.id))

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

    def test_delete_other_users_recipe_not_working(self):
        """ Test trying to delete another user's recipe doesn't work """
        new_user = create_user(email='testuser2@example.com', password='Test1234')
        recipe = create_recipe(user=new_user)
        res = self.client.delete(detail_url(recipe.id))

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())

    def test_create_recipe_with_new_tags(self):
        """ Test creating a recipe with new tags """
        payload = {
            'title': 'Thai Prawn Curry',
            'time_minutes': 30,
            'price': Decimal('2.50'),
            'tags': [{'name': 'Thai'}, {'name': 'Dinner'}]
        }
        # When providing nested objects, we need to specify the format=json, to make sure it will be converted to json.
        res = self.client.post(RECIPES_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipes = Recipe.objects.filter(user=self.user)

        # This 2 lines provide same result, len would be better here because we already saved objects to our memory.
        # Count method executes a query to the DB -> performs a SELECT COUNT(*)
        self.assertEqual(recipes.count(), 1)
        self.assertEqual(len(recipes), 1)

        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)

        for tag in payload['tags']:
            exists = recipe.tags.filter(name=tag['name'], user=self.user).exists()
            self.assertTrue(exists)

    def test_create_recipe_with_existing_tags(self):
        """ Test creating a recipe with existing tags """
        tag_indian = Tag.objects.create(user=self.user, name='Indian')
        payload = {
            'title': 'Pongal',
            'time_minutes': 60,
            'price': Decimal('4.50'),
            'tags': [{'name': 'Indian'}, {'name': 'Breakfast'}]
        }
        res = self.client.post(RECIPES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)

        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)
        self.assertIn(tag_indian, recipe.tags.all())

        tags = Tag.objects.filter(user=self.user)
        self.assertEqual(tags.count(), 2)

        for tag in payload['tags']:
            exists = recipe.tags.filter(
                name=tag['name'],
                user=self.user
            ).exists()
            self.assertTrue(exists)

    def test_create_tag_on_update(self):
        """ Test creating a tag when updating a recipe """
        recipe = create_recipe(user=self.user)
        payload = {
            'tags': [{'name': 'Vegan'}, {'name': 'Dinner'}]
        }
        self.assertEqual(len(recipe.tags.all()), 0)
        # self.assertEqual(Tag.objects.count(), 0)
        # self.assertFalse(recipe.tags.exists())

        res = self.client.patch(detail_url(recipe.id), payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        recipe.refresh_from_db()  # Check if I need it
        for tag in payload['tags']:
            exists = recipe.tags.filter(name=tag['name'], user=self.user).exists()
            self.assertTrue(exists)

        # self.assertEqual(res.data['tags'], payload['tags']) # Check if it works
        # self.assertEqual(recipe.tags.values(), res.data['tags']) # Check if it works
        # self.assertEqual(recipe.tags.values(), payload['tags']) # Check if it works

    def test_update_recipe_assign_tag(self):
        """ Test assigning an existing tag when updating a recipe """
        tag_breakfast = Tag.objects.create(user=self.user, name='Breakfast')
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag_breakfast)

        tag_lunch = Tag.objects.create(user=self.user, name='Lunch')
        payload = {'tags': [{'name': 'Lunch'}]}
        res = self.client.patch(detail_url(recipe.id), payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(tag_lunch, recipe.tags.all())
        self.assertNotIn(tag_breakfast, recipe.tags.all())
        # self.assertEqual(Tag.objects.count(), 2)  # Moje, sprawdzić czy działa, czy na pewno nie zduplikował się Tag (sprwadzić to jak wszystkie testy będą przechodzić)

    def test_clear_recipe_tags(self):
        """ Test clearing a recipes tags """
        tag = Tag.objects.create(user=self.user, name='Vegan')
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag)
        payload = {'tags': []}

        res = self.client.patch(detail_url(recipe.id), payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # self.assertFalse(recipe.tags.exists()) # Check if works
        self.assertEqual(recipe.tags.count(), 0)
