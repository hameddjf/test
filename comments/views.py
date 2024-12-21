from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import Comment, Like
from .serializers import CommentSerializer, LikeSerializer
from .permissions import IsAuthorOrReadOnly


class CommentListCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request):
        blog_id = request.query_params.get('blog_id')
        product_id = request.query_params.get('product_id')

        comments = Comment.objects.filter(is_active=True)

        if blog_id:
            comments = comments.filter(blog_id=blog_id)
        elif product_id:
            comments = comments.filter(product_id=product_id)

        serializer = CommentSerializer(
            comments,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)

    def post(self, request):
        serializer = CommentSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            # Checking whether the comment is for the blog or the product
            if 'blog' in request.data and 'product' in request.data:
                return Response(
                    {"error": "Cannot comment on both blog and product"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentDetailAPIView(APIView):
    permission_classes = [IsAuthorOrReadOnly]

    def get_object(self, pk):
        return get_object_or_404(Comment, pk=pk, is_active=True)

    def get(self, request, pk):
        comment = self.get_object(pk)
        serializer = CommentSerializer(comment, context={'request': request})
        return Response(serializer.data)

    @transaction.atomic
    def put(self, request, pk):
        comment = self.get_object(pk)
        self.check_object_permissions(request, comment)

        serializer = CommentSerializer(
            comment,
            data=request.data,
            context={'request': request},
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        comment = self.get_object(pk)
        self.check_object_permissions(request, comment)
        comment.is_active = False
        comment.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class LikeCreateDestroyAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request, comment_id):
        serializer = LikeSerializer(
            data={'comment': comment_id, **request.data}, context={'request': request}
        )

        if serializer.is_valid():
            try:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except ValidationError as e:
                return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, comment_id):
        like = get_object_or_404(
            Like,
            user=request.user,
            comment_id=comment_id,
            is_active=True
        )
        like.is_active = False
        like.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
