from rest_framework import viewsets, status
from .models import Product, Order, Supplier, OrderItem, Contact, Cart
from .serializers import ProductSerializer, OrderSerializer, SupplierSerializer, ContactSerializer
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from .serializers import UserSerializer
from rest_framework.permissions import IsAuthenticated
from .serializers import CartSerializer
from rest_framework import generics
from rest_framework.decorators import action
import logging
from .utils import send_order_confirmation


logger = logging.getLogger(__name__)

class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart_items = Cart.objects.filter(owner=request.user)
        serializer = CartSerializer(cart_items, many=True)
        return Response(serializer.data)

    def post(self, request):
        product_id = request.data.get('product')
        quantity = request.data.get('quantity', 1)
        product = Product.objects.get(id=product_id)

        cart_item, created = Cart.objects.get_or_create(owner=request.user, product=product)
        cart_item.quantity = quantity
        cart_item.save()

        serializer = CartSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, cart_id):
        try:
            cart_item = Cart.objects.get(id=cart_id, owner=request.user)
            cart_item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Cart.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(buyer=self.request.user)

    @action(detail=False, methods=['post'], url_path='confirm')
    def confirm_order(self, request):
        cart_id = request.data.get('cart_id')
        contact_id = request.data.get('contact_id')

        logging.debug(f"Confirm order request data: cart_id={cart_id}, contact_id={contact_id}")

        if not cart_id or not contact_id:
            return Response({"error": "Cart ID and Contact ID are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            cart = get_object_or_404(Cart, id=cart_id, owner=request.user)
            contact = get_object_or_404(Contact, id=contact_id, user=request.user)

            logging.debug(f"Cart retrieved: {cart}, Contact retrieved: {contact}")

            # Create the order and link the contact
            order = Order.objects.create(buyer=request.user, contact_info=contact, status='confirmed')

            for cart_item in cart.items.all():
                logging.debug(f"Processing cart item: {cart_item}")
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price
                )

            # Clear the cart after order confirmation
            cart.items.all().delete()
            logging.debug(f"Cart {cart_id} cleared after order confirmation.")

            send_order_confirmation(order, contact.email)

            return Response({"status": "Order confirmed successfully", "order_id": order.id}, status=status.HTTP_201_CREATED)

        except Exception as e:
            logging.error(f"An error occurred: {e}")
            return Response({"error": "An error occurred while confirming the order"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['patch'], url_path='update-status')
    def update_status(self, request, pk=None):
        """
        Custom action to update the order status.
        Example request: PATCH /orders/{id}/update-status/
        """
        order = get_object_or_404(Order, id=pk, buyer=request.user)
        new_status = request.data.get('status')

        if new_status not in dict(Order.STATUS_CHOICES):
            return Response({"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)

        order.status = new_status
        order.save()

        return Response({"status": f"Order status updated to {new_status}"}, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        try:
            # Get the specific order for the authenticated user
            order = get_object_or_404(Order, id=pk, buyer=request.user)
            serializer = OrderSerializer(order)
            return Response(serializer.data)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)


class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer


