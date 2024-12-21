from django.urls import path
from .views import RatingListCreateAPIView, RatingDetailAPIView

urlpatterns = [
    path('', RatingListCreateAPIView.as_view(), name='rating-list-create'),
    path('<int:pk>/', RatingDetailAPIView.as_view(), name='rating-detail'),
]
