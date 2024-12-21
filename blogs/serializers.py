from rest_framework import serializers

from .models import Blog

from comments.serializers import CommentSerializer


class BlogListSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = Blog
        fields = ['id', 'title', 'poster', 'user', 'publish', 'slug']


class BlogDetailSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    comments = CommentSerializer(many=True, read_only=True)
    created = serializers.DateTimeField(format="%Y-%m-%d %H:%M")
    updated = serializers.DateTimeField(format="%Y-%m-%d %H:%M")

    class Meta:
        model = Blog
        fields = ['id', 'title', 'description', 'poster', 'user',
                  'publish', 'slug', 'created', 'updated', 'comments']
