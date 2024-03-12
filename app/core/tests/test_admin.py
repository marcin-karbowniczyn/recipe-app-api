""" Tests for the Django Admin modifications """
from django.test import TestCase, Client, SimpleTestCase
from django.contrib.auth import get_user_model
from django.urls import reverse


class AdminSiteTests(TestCase):
    """ Tests for Django Admin """

    # This is called immediately before calling the test method
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
        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)
