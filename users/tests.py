from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class UserTests(APITestCase):

    def setUp(self):
        self.email = "test@example.com"
        self.password = "password123"

        self.register_url = reverse("user:create")
        self.token_url = reverse("user:token_obtain_pair")
        self.me_url = reverse("user:manage")

    def test_create_user(self):
        data = {
            "email": "newuser@example.com",
            "password": "securepassword",
            "first_name": "Ivan",
            "last_name": "Ivanov",
        }
        response = self.client.post(self.register_url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email="newuser@example.com").exists())

    def test_create_user_password_not_in_response(self):
        data = {
            "email": "newuser@example.com",
            "password": "securepassword",
        }
        response = self.client.post(self.register_url, data)

        self.assertNotIn("password", response.data)

    def test_create_user_with_same_email(self):
        User.objects.create_user(email=self.email, password=self.password)

        data = {"email": self.email, "password": "password456"}
        response = self.client.post(self.register_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_token(self):
        User.objects.create_user(email=self.email, password=self.password)

        data = {"email": self.email, "password": self.password}
        response = self.client.post(self.token_url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_get_token_wrong_password(self):
        User.objects.create_user(email=self.email, password=self.password)

        data = {"email": self.email, "password": "wrongpassword"}
        response = self.client.post(self.token_url, data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_without_token(self):
        response = self.client.get(self.me_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_profile(self):
        User.objects.create_user(email=self.email, password=self.password)

        token_response = self.client.post(
            self.token_url, {"email": self.email, "password": self.password}
        )
        access_token = token_response.data["access"]

        # в settings header змінений на Authorize
        response = self.client.get(self.me_url, HTTP_AUTHORIZE=f"Bearer {access_token}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.email)

    def test_update_profile(self):
        User.objects.create_user(email=self.email, password=self.password)

        token_response = self.client.post(
            self.token_url, {"email": self.email, "password": self.password}
        )
        access_token = token_response.data["access"]

        response = self.client.patch(
            self.me_url,
            {"first_name": "Petro"},
            HTTP_AUTHORIZE=f"Bearer {access_token}",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["first_name"], "Petro")

    def test_create_user_without_email(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email="", password=self.password)

    def test_create_superuser(self):
        admin = User.objects.create_superuser(
            email="admin@example.com", password="adminpass123"
        )

        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)