""" Tests for the Django Admin modifications """
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class AdminSiteTests(TestCase):
    """ Tests for Django Admin """

    # This is called immediately before calling every test method
    def setUp(self):
        """ Create user and client """
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(email='admin@example.com', password='test1234')
        self.client.force_login(self.admin_user)

        self.user = get_user_model().objects.create_user(email='user@example.com', password='test1234', name='Test User')

    def test_users_list(self):
        """ Test that users are listed on a page """
        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)

        # These methods are implemented by Django Test system
        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_edit_user_page(self):
        """ Test that edit users page works """
        # url -> /admin/core/user/1/change/
        url = reverse('admin:core_user_change', args=[self.user.id])  # user that is created in setUp
        res = self.client.get(url)

        # To make sure the page loads sucesfully, we check if the status_code is 200
        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self):
        """ Test if the creater user page works """
        url = reverse('admin:core_user_add')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
