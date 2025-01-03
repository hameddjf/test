from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # پروفایل
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/update/', views.ProfileUpdateView.as_view(), name='profile-update'),
    
    # سفارشات
    path('orders/', views.OrderHistoryView.as_view(), name='order-history'),
    
    # آدرس‌ها
    path('addresses/', views.AddressCreateView.as_view(), name='address-list'),
    path('addresses/<int:pk>/', views.AddressDetailView.as_view(), name='address-detail'),
]