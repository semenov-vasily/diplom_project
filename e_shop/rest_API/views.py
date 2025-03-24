from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import get_object_or_404
import logging

from .models import Product, Order, Supplier, OrderItem, Contact, Cart
from .serializers import (
    ProductSerializer, OrderSerializer, SupplierSerializer,
    ContactSerializer, UserSerializer, CartSerializer
)
from .tasks import send_order_email


logger = logging.getLogger(__name__)


class ShoppingCartView(APIView):
    """
    Представление для управления корзиной покупок.

    GET: Возвращает список элементов корзины текущего пользователя.
    POST: Добавляет или обновляет элемент корзины.
    DELETE: Удаляет элемент корзины по ID.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart_items = Cart.objects.filter(owner=request.user)
        serializer = CartSerializer(cart_items, many=True)
        return Response(serializer.data)

    def post(self, request):
        product_id = request.data.get('product')
        quantity = int(request.data.get('quantity', 1))
        product = get_object_or_404(Product, id=product_id)

        cart_item, created = Cart.objects.get_or_create(owner=request.user, product=product)
        cart_item.quantity = quantity
        cart_item.save()

        serializer = CartSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, cart_id):
        cart_item = get_object_or_404(Cart, id=cart_id, owner=request.user)
        cart_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RegisterView(APIView):
    """
    Представление для регистрации новых пользователей.

    POST: Регистрирует пользователя, используя переданные данные.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        logger.debug("RegisterView POST вызван")
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Пользователь успешно создан'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductViewSet(viewsets.ModelViewSet):
    """
    Представление для работы с товарами.

    Позволяет выполнять CRUD-операции, а также фильтровать товары по ID поставщика.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_queryset(self):
        supplier_id = self.request.query_params.get('supplier')
        if supplier_id:
            return self.queryset.filter(supplier_id=supplier_id)
        return self.queryset


class OrderViewSet(viewsets.ModelViewSet):
    """
    Представление для управления заказами.

    GET: Возвращает заказы текущего пользователя.
    POST (action confirm): Подтверждает заказ, создавая заказ по данным корзины и контакта.
    PATCH (action update-status): Обновляет статус заказа.
    """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(buyer=self.request.user)

    @action(detail=False, methods=['post'], url_path='confirm')
    def confirm_order(self, request):
        cart_id = request.data.get('cart_id')
        contact_id = request.data.get('contact_id')
        logger.debug(f"Confirm order request: cart_id={cart_id}, contact_id={contact_id}")

        if not cart_id or not contact_id:
            return Response({"error": "Необходимы ID корзины и контакта."}, status=status.HTTP_400_BAD_REQUEST)

        cart = get_object_or_404(Cart, id=cart_id, owner=request.user)
        contact = get_object_or_404(Contact, id=contact_id, user=request.user)
        logger.debug(f"Получена корзина: {cart}, получен контакт: {contact}")

        order = Order.objects.create(buyer=request.user, contact_info=contact, status='confirmed')
        for cart_item in cart.items.all():
            logger.debug(f"Обработка элемента корзины: {cart_item}")
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )

        # Очищаем корзину после подтверждения заказа
        cart.items.all().delete()
        logger.debug(f"Корзина {cart_id} очищена после подтверждения заказа.")
        # send_order_mail_confirm(order, contact.email)
        send_order_email.delay(order.id, contact.email)
        return Response({"status": "Заказ успешно подтвержден", "order_id": order.id}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['patch'], url_path='update-status')
    def update_status(self, request, pk=None):
        order = get_object_or_404(Order, id=pk, buyer=request.user)
        new_status = request.data.get('status')
        if new_status not in dict(Order.STATUS_CHOICES):
            return Response({"error": "Неверный статус"}, status=status.HTTP_400_BAD_REQUEST)
        order.status = new_status
        order.save()
        return Response({"status": f"Статус заказа обновлен на {new_status}"}, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        order = get_object_or_404(Order, id=pk, buyer=request.user)
        serializer = OrderSerializer(order)
        return Response(serializer.data)


class SupplierViewSet(viewsets.ModelViewSet):
    """
    Представление для работы с поставщиками.
    """
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer


class ContactView(APIView):
    """
    Представление для управления контактами пользователя.

    GET: Возвращает список контактов.
    POST: Создает новый контакт или обновляет существующий (если передан 'id').
    DELETE: Удаляет контакт по ID.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        contacts = Contact.objects.filter(user=request.user)
        serializer = ContactSerializer(contacts, many=True)
        return Response(serializer.data)

    def post(self, request):
        contact_id = request.data.get('id')
        if contact_id:
            contact = get_object_or_404(Contact, id=contact_id, user=request.user)
            serializer = ContactSerializer(contact, data=request.data)
            if serializer.is_valid():
                serializer.save(user=request.user)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            serializer = ContactSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, contact_id):
        contact = get_object_or_404(Contact, id=contact_id, user=request.user)
        contact.delete()
        return Response({"message": "Контакт успешно удален"}, status=status.HTTP_204_NO_CONTENT)


class OrderListView(generics.ListAPIView):
    """
    Представление для получения списка заказов текущего пользователя.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(buyer=self.request.user)