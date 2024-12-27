from django.urls import path

from . import views

from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('signup/', views.SignUpView.as_view(), name='signup_api'),
    
    path('activate/<uidb64>/<token>/',views.ActivateAccountView.as_view(), name='activate'),
    
    path('login/', views.CustomLoginView.as_view(), name='login_api'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout_api'),
    
    path('change_password/', views.CustomPasswordChangeView.as_view(),name='change_password'),
    
    path('profile/', views.ProfileUpdateView.as_view(), name='profile_api'),
    
    path('token/', TokenObtainPairView.as_view(),name='token_obtain_pair'),  # دریافت توکن JWT
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # رفرش توکن JWT

    path('contact/', views.ContactView.as_view(), name='contact'),
]
