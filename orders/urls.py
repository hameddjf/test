from django.urls import path

from . import views

app_name = 'orders'

urlpatterns = [
     path('',
         views.OrderListCreateAPIView.as_view(),
         name='order-list-create'),

     path('<int:pk>/',
         views.OrderDetailAPIView.as_view(),
         name='order-detail'),

     path('<int:pk>/cancel/',
         views.OrderCancelAPIView.as_view(),
         name='order-cancel'),

     path('<int:pk>/process-payment/',
         views.OrderProcessPaymentAPIView.as_view(),
         name='order-process-payment'),

     path('create/', views.OrderCreateAPIView.as_view(), name='order-create'),
    
     path('addresses/', views.AddressListCreateView.as_view(), name='address-list-create'),
     path('addresses/<int:pk>/', views.AddressDetailView.as_view(), name='address-detail'),
]