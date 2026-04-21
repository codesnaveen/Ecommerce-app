from django.urls import path
from .views import (
    CartView, CartItemAddView, CartItemUpdateView,
    CheckoutView, OrderListView, OrderDetailView
)

urlpatterns = [
    path('cart/', CartView.as_view(), name='cart'),
    path('cart/add/', CartItemAddView.as_view(), name='cart-add'),
    path('cart/items/<int:item_id>/', CartItemUpdateView.as_view(), name='cart-item'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('', OrderListView.as_view(), name='order-list'),
    path('<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
]
