from django.urls import path
from . import views

app_name = 'comments'

urlpatterns = [
    path('', views.CommentListCreateAPIView.as_view(),
         name='comment-list-create'),
    path('<int:pk>/', views.CommentDetailAPIView.as_view(),
         name='comment-detail'),
    path('<int:comment_id>/reaction/',
         views.LikeCreateDestroyAPIView.as_view(), name='comment-reaction'),
]
