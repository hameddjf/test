from rest_framework import serializers

from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from .models import Comment, Like

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Comment, Like

User = get_user_model()


class UserBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username')


class CommentSerializer(serializers.ModelSerializer):
    author = UserBriefSerializer(read_only=True)
    like_count = serializers.SerializerMethodField()
    dislike_count = serializers.SerializerMethodField()
    user_reaction = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            'id', 'product', 'author', 'body', 'blog''created_at', 'updated_at', 'is_active',
            'like_count', 'dislike_count', 'user_reaction'
        ]
        read_only_fields = ['author', 'created_at', 'updated_at', 'is_active']

    def get_like_count(self, obj):
        return obj.likes.filter(is_active=True, reaction_type='like').count()

    def get_dislike_count(self, obj):
        return obj.likes.filter(is_active=True, reaction_type='dislike').count()

    def get_user_reaction(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            reaction = obj.likes.filter(
                user=request.user, is_active=True
            ).values_list('reaction_type', flat=True).first()
            return reaction
        return None


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'comment', 'reaction_type', 'created_at']
        read_only_fields = ['created_at']

    def validate(self, data):
        user = self.context['request'].user
        comment = data['comment']
        reaction_type = data['reaction_type']

        existing_reaction = Like.objects.filter(
            user=user, comment=comment, is_active=True).first()

        if self.instance is None and existing_reaction:
            if existing_reaction.reaction_type == reaction_type:
                raise serializers.ValidationError(
                    _('You have already reacted to this comment.'))
            else:
                existing_reaction.is_active = False
                existing_reaction.save()

        return data

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
