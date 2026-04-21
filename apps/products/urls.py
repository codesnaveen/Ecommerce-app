from django.urls import path
from .views import (
    CategoryListView, ProductListView, ProductDetailView,
    FeaturedProductsView, ReviewListCreateView,
    WishlistView, WishlistDeleteView,
    SellerProductListView, SellerProductCreateView
)

urlpatterns = [
    path('', ProductListView.as_view(), name='product-list'),
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('featured/', FeaturedProductsView.as_view(), name='featured-products'),
    path('<slug:slug>/', ProductDetailView.as_view(), name='product-detail'),
    path('<slug:slug>/reviews/', ReviewListCreateView.as_view(), name='product-reviews'),
    path('wishlist/', WishlistView.as_view(), name='wishlist'),
    path('wishlist/<int:product_id>/', WishlistDeleteView.as_view(), name='wishlist-delete'),
    path('seller/products/', SellerProductListView.as_view(), name='seller-products'),
    path('seller/products/create/', SellerProductCreateView.as_view(), name='seller-product-create'),
]
