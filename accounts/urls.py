from django.urls import path

from . import views

from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('api/signup/', views.SignUpView.as_view(), name='signup_api'),
    path('api/activate/<uidb64>/<token>/',
         views.ActivateAccountView.as_view(), name='activate'),
    path('api/login/', views.CustomLoginView.as_view(), name='login_api'),
    path('api/logout/', views.CustomLogoutView.as_view(), name='logout_api'),
    path('api/change_password', views.CustomPasswordChangeView.as_view(),
         name='change_password'),
    path('api/profile/', views.ProfileUpdateView.as_view(), name='profile_api'),
    path('api/token/', TokenObtainPairView.as_view(),
         name='token_obtain_pair'),  # دریافت توکن JWT
    path('api/token/refresh/', TokenRefreshView.as_view(),
         name='token_refresh'),  # رفرش توکن JWT

    path('contact/', views.ContactView.as_view(), name='contact'),
]
