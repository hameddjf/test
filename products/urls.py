from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # Category
    path('categories/', views.CategoryListCreateAPIView.as_view(),
         name='category-list'),
    path('categories/<slug:slug>/',
         views.CategoryDetailAPIView.as_view(), name='category-detail'),

    # Product Gallery
    path('product-galleries/', views.ProductGalleryListCreateAPIView.as_view(),
         name='product-gallery-list'),

    # Product
    path('products/', views.ProductListCreateAPIView.as_view(), name='product-list'),
    path('products/<slug:slug>/',
         views.ProductDetailAPIView.as_view(), name='product-detail'),
    path('products/single/<slug:slug>/',
         views.ProductSingleAPIView.as_view(), name='product-single'),
    # search
    path('product-search/', views.ProductSearchView.as_view(), name='product-search'),
]
