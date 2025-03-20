from django.core.management import call_command
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient


class ShopAPITests(TestCase):
    def test_products_list(self):
        # Проверка получения списка товаров
        response = self.client.get('/products/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.data) > 0, "Список товаров не должен быть пустым.")

    def test_product_detail(self):
        # Проверка деталей товара: получим ID первого товара из списка
        products_response = self.client.get('/products/')
        self.assertEqual(products_response.status_code, 200)
        if products_response.data:
            first_product_id = products_response.data[0]['id']
            detail_response = self.client.get(f'/products/{first_product_id}/')
            self.assertEqual(detail_response.status_code, 200)
            self.assertEqual(detail_response.data['id'], first_product_id)
        else:
            self.fail("Нет товаров для теста деталей.")

    def test_product_filtering_by_supplier(self):
        # Предположим, что в фикстуре есть поставщик с id=1
        response = self.client.get('/products/?supplier=1')
        self.assertEqual(response.status_code, 200)
        for product in response.data:
            self.assertEqual(product.get('supplier'), 1)

    def test_authentication_login_logout(self):
        # Тестирование эндпоинтов для входа и выхода
        # Логин
        login_data = {'username': 'testuser', 'password': 'testpass'}
        login_response = self.client.post('/auth/login/', login_data, format='json')
        self.assertEqual(login_response.status_code, 200)
        # После логина можно проверить, например, наличие токена в ответе (если реализовано)

        # Выход
        logout_response = self.client.post('/auth/logout/')
        self.assertEqual(logout_response.status_code, 200)

    def test_orders_list(self):
        # Проверка получения списка заказов
        response = self.client.get('/orders/')
        self.assertEqual(response.status_code, 200)

    def test_order_detail(self):
        # Если заказы есть, проверим детали первого заказа
        orders_response = self.client.get('/orders/')
        self.assertEqual(orders_response.status_code, 200)
        if orders_response.data:
            first_order_id = orders_response.data[0]['id']
            detail_response = self.client.get(f'/orders/{first_order_id}/')
            self.assertEqual(detail_response.status_code, 200)
            self.assertEqual(detail_response.data['id'], first_order_id)
        else:
            self.fail("Нет заказов для проверки деталей.")

    def test_order_confirm(self):
        # Тест подтверждения заказа
        # Здесь предполагается, что эндпоинт ожидает, например, идентификатор заказа
        response = self.client.post('/orders/confirm/', {'order_id': 1}, format='json')
        self.assertIn(response.status_code, [200, 201], "Подтверждение заказа должно вернуть 200 или 201.")

    def test_order_update_status(self):
        # Тест обновления статуса заказа
        orders_response = self.client.get('/orders/')
        self.assertEqual(orders_response.status_code, 200)
        if orders_response.data:
            first_order_id = orders_response.data[0]['id']
            # Предположим, что обновление статуса происходит через PATCH с новым значением поля status
            response = self.client.patch(f'/orders/{first_order_id}/update-status/',
                                         {'status': 'confirmed'}, format='json')
            self.assertEqual(response.status_code, 200)
        else:
            self.fail("Нет заказов для проверки обновления статуса.")

    def test_cart_management(self):
        # Тестирование эндпоинта для управления корзиной
        get_response = self.client.get('/cart/')
        self.assertEqual(get_response.status_code, 200)
        # Пример добавления товара в корзину:
        post_response = self.client.post('/cart/', {'product_id': 1, 'quantity': 2}, format='json')
        self.assertEqual(post_response.status_code, 200)

    def test_contacts(self):
        # Проверка получения списка контактов
        list_response = self.client.get('/contacts/')
        self.assertEqual(list_response.status_code, 200)
        if list_response.data:
            first_contact_id = list_response.data[0]['id']
            detail_response = self.client.get(f'/contacts/{first_contact_id}/')
            self.assertEqual(detail_response.status_code, 200)
        else:
            self.fail("Нет контактов для проверки деталей.")