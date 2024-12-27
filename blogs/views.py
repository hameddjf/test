from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from django.shortcuts import get_object_or_404

from .models import Blog
from .serializers import BlogListSerializer, BlogDetailSerializer

# Create your views here.


class BlogAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, slug=None):
        if slug:
            blog = get_object_or_404(Blog, slug=slug)
            serializer = BlogDetailSerializer(blog)
            return Response(serializer.data)

        blogs = Blog.objects.filter(publish=True)
        serializer = BlogListSerializer(blogs, many=True)
        return Response(serializer.data)

    # def post(self, request):
    #     serializer = BlogDetailSerializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save(user=request.user)
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # def put(self, request, slug):
    #     blog = get_object_or_404(Blog, slug=slug)
    #     if blog.user != request.user:
    #         return Response(status=status.HTTP_403_FORBIDDEN)

    #     serializer = BlogDetailSerializer(blog, data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # def delete(self, request, slug):
    #     blog = get_object_or_404(Blog, slug=slug)
    #     if blog.user != request.user:
    #         return Response(status=status.HTTP_403_FORBIDDEN)

    #     blog.delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)
