from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # Category
    path('categories/', views.CategoryListAPIView.as_view(),name='category-list'),
#     path('categories/<slug:slug>/',views.CategoryDetailAPIView.as_view(), name='category-detail'),

    # Product Gallery
    path('product-galleries/', views.ProductGalleryListAPIView.as_view(),name='product-gallery-list'),

    # Product
    path('products/', views.ProductListAPIView.as_view(), name='product-list'),
    path('products/<slug:slug>/',views.ProductDetailAPIView.as_view(), name='product-detail'),
    # search
#     path('product-search/', views.ProductSearchView.as_view(), name='product-search'),
]
