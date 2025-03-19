from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import  OrderViewSet, SupplierViewSet, CartView
from rest_framework.authtoken.views import obtain_auth_token


api_router = DefaultRouter()
api_router.register(r'orders', OrderViewSet, basename='order')
api_router.register(r'suppliers', SupplierViewSet, basename='supplier')


urlpatterns = [
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    path('', include(api_router.urls)),
    path('cart/', CartView.as_view(), name='cart')
    ]

