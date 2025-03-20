from django.urls import path, include
from django.contrib import admin
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, OrderViewSet, SupplierViewSet, ContactView, OrderListView, RegisterView, CartView
from rest_framework.authtoken.views import obtain_auth_token
from django.http import HttpResponse


api_router = DefaultRouter()
api_router.register(r'products', ProductViewSet, basename='product')
api_router.register(r'orders', OrderViewSet, basename='order')
api_router.register(r'suppliers', SupplierViewSet, basename='supplier')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', RegisterView.as_view(), name='register'),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    path('', include(api_router.urls)),
    path('cart/', CartView.as_view(), name='cart'),
    path('contacts/', ContactView.as_view(), name='contacts'),
    path('orders/', OrderListView.as_view(), name='order-list'),
    path('contacts/<int:contact_id>/', ContactView.as_view(), name='contact-delete'),
]

urlpatterns += [
    path('test/', lambda request: HttpResponse("Test OK"), name='test'),
]