from django.urls import path

from . import views

app_name = 'carts'

urlpatterns = [
    # promotions
    path('promotions/', views.PromotionListView.as_view(), name='promotion-list'),
     # path('promotions/<int:pk>/', views.PromotionDetailView.as_view(),name='promotion-detail'),

    # cart
#     path('', views.CartItemListView.as_view(), name='cart-list'),
#     path('cart/<int:pk>/', views.CartItemDetailView.as_view(), name='cart-detail'),

    # coupon
    path('coupon/', views.CouponView.as_view(),name='coupon'),
    # path('validate-coupon/', views.ValidateCouponView.as_view(),name='validate-coupon'),
    # path('apply-coupon/', views.ApplyCouponView.as_view(), name='apply-coupon'),
]
