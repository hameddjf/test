from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.BlogAPIView.as_view(), name='blog-list'),
    path('<slug:slug>/', views.BlogAPIView.as_view(), name='blog-detail'),
]
