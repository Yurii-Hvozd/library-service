from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from books.models import Book

User = get_user_model()


class BookApiTests(APITestCase):

    def setUp(self):
        self.list_url = reverse("books:book-list")

        self.book_data = {
            "title": "The Hobbit",
            "author": "J.R.R. Tolkien",
            "cover": "HARD",
            "inventory": 5,
            "daily_fee": "2.99",
        }

        # адмін, який буде робити запити
        self.admin = User.objects.create_superuser(
            email="admin@example.com", password="adminpass123"
        )
        self.client.force_authenticate(user=self.admin)

    def test_create_book(self):
        response = self.client.post(self.list_url, self.book_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 1)
        self.assertEqual(Book.objects.get().title, "The Hobbit")

    def test_create_book_with_negative_inventory(self):
        self.book_data["inventory"] = -1

        response = self.client.post(self.list_url, self.book_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Book.objects.count(), 0)

    def test_get_book_list(self):
        Book.objects.create(**self.book_data)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "The Hobbit")

    def test_get_book_detail(self):
        book = Book.objects.create(**self.book_data)
        detail_url = reverse("books:book-detail", kwargs={"pk": book.id})

        response = self.client.get(detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["author"], "J.R.R. Tolkien")
        self.assertEqual(response.data["cover"], "HARD")

    def test_get_book_detail_not_found(self):
        detail_url = reverse("books:book-detail", kwargs={"pk": 999})

        response = self.client.get(detail_url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_book(self):
        book = Book.objects.create(**self.book_data)
        detail_url = reverse("books:book-detail", kwargs={"pk": book.id})

        response = self.client.patch(detail_url, {"inventory": 10})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        book.refresh_from_db()
        self.assertEqual(book.inventory, 10)

    def test_delete_book(self):
        book = Book.objects.create(**self.book_data)
        detail_url = reverse("books:book-detail", kwargs={"pk": book.id})

        response = self.client.delete(detail_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Book.objects.count(), 0)