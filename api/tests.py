from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from lists.models import TodoList


class UserTests(APITestCase):
    def setUp(self):
        User.objects.create_user("test", "test@example.com", "test")
        self.client.login(username="test", password="test")

    def tearDown(self):
        User.objects.get(username="test").delete()
        self.client.logout()

    def test_post_on_read_only(self):
        response = self.client.post("api:user-list", {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_user_if_not_admin(self):
        get_response = self.client.get("/api/users/{}/".format(1))
        self.assertEqual(get_response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_user_if_admin(self):
        User.objects.create_superuser("admin", "admin@example.com", "admin")
        self.client.login(username="admin", password="admin")
        get_response = self.client.get("/api/users/{}/".format(1))
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_response.data["username"], "test")
