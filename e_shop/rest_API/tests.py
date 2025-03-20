from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from .models import Supplier, Product


class ProductsListTest(TestCase):
    """
    тестовый класс, который регистрирует и авторизует пользователя,
    создаёт тестовый товар, а затем отправляет запрос GET к эндпоинту
    /products/ и проверяет, что в ответе возвращается список с хотя
    бы одним товаром.
    """
    def setUp(self):
        self.client = APIClient()
        # Регистрируем пользователя
        response = self.client.post(
            '/register/',
            {
                "username": "testuser",
                "email": "testuser@example.com",
                "password": "testpassword123"
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Логинимся и получаем токен
        response = self.client.post(
            '/api-token-auth/',
            {
                "username": "testuser",
                "password": "testpassword123"
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token = response.data.get("token")
        self.assertIsNotNone(token)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        # Создаем тестовый товар.

        self.supplier = Supplier.objects.create(name="Test Supplier")
        self.product = Product.objects.create(
            title="Test Product",
            supplier=self.supplier,
            price=100.00,
            quantity=10,
            parameters={"color": "red"}
        )

    def test_get_products(self):
        response = self.client.get('/products/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Проверяем, что возвращается список товаров с хотя бы одним товаром.
        self.assertTrue(isinstance(response.data, list))
        self.assertTrue(len(response.data) >= 1)