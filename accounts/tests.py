from django import forms
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from accounts.forms import LoginForm, RegistrationForm


class AccountsTests(TestCase):
    def setUp(self):
        self.register_data = {
            "email": "new@user.com",
            "username": "new_user",
            "password": "test",
            "password_confirmation": "test",
        }
        User.objects.create_user("test", "test@example.com", "test")

    def tearDown(self):
        User.objects.get(username="test").delete()

    def test_get_register(self):
        response = self.client.get(reverse("auth:register"))
        self.assertTemplateUsed(response, "accounts/register.html")
        self.assertIsInstance(response.context["form"], RegistrationForm)

    def test_get_login(self):
        response = self.client.get(reverse("auth:login"))
        self.assertTemplateUsed(response, "accounts/login.html")
        self.assertIsInstance(response.context["form"], LoginForm)

    def test_register(self):
        response = self.client.post(reverse("auth:register"),
                                    data=self.register_data)
        self.assertRedirects(response, "/auth/login/")
        self.assertIsNotNone(User.objects.get(username="new_user"))

    def test_login(self):
        self.assertFalse("_auth_user_id" in self.client.session)
        login_data = {"username": "test", "password": "test"}
        response = self.client.post(reverse("auth:login"), data=login_data)
        self.assertRedirects(response, "/")
        # user is logged in
        self.assertEqual(self.client.session["_auth_user_id"], "1")

    def test_faulty_login(self):
        login_data = {"username": 65 * "X", "password": "test"}
        response = self.client.post(reverse("auth:login"), data=login_data)
        error_message = "Ensure this value has at most 64 characters"
        self.assertContains(response, error_message, status_code=200)

    def test_login_with_non_existent_user(self):
        login_data = {"username": "notauser", "password": "stillapassowrd"}
        response = self.client.post(reverse("auth:login"), data=login_data)
        error_message = "Incorrect username and/or password."
        self.assertContains(response, error_message, status_code=200)

    def test_login_with_wrong_password(self):
        login_data = {"username": "test", "password": "wrongpassword"}
        response = self.client.post(reverse("auth:login"), data=login_data)
        error_message = "Incorrect username and/or password."
        self.assertContains(response, error_message, status_code=200)

    def test_faulty_register(self):
        self.register_data["username"] = 65 * "X"
        response = self.client.post(reverse("auth:register"),
                                    data=self.register_data)
        error_message = "Ensure this value has at most 64 characters"
        self.assertContains(response, error_message, status_code=200)

    def test_logout(self):
        response = self.client.get(reverse("auth:logout"))
        self.assertRedirects(response, "/")
        self.assertFalse("_auth_user_id" in self.client.session)
