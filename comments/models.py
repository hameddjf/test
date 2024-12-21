from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class Comment(models.Model):
    product = models.ForeignKey(
        'products.Product', related_name='comments', on_delete=models.CASCADE,
        verbose_name=_('product'), help_text=_('The product this comment belongs to'))

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='product_comments', on_delete=models.CASCADE,
        verbose_name=_('author'), help_text=_('User who wrote the comment'))
    blog = models.ForeignKey(
        'blogs.Blog', on_delete=models.CASCADE, related_name='comments', null=True,
        blank=True, default=None)
    body = models.TextField(
        verbose_name=_('comment text'), help_text=_('The content of the comment'), max_length=1000)

    created_at = models.DateTimeField(
        default=timezone.now, verbose_name=_('created at'), db_index=True)

    updated_at = models.DateTimeField(
        auto_now=True, verbose_name=_('updated at'))

    is_active = models.BooleanField(
        default=True, verbose_name=_('active status'), help_text=_('comment is active or soft deleted'))

    class Meta:
        verbose_name = _('comment')
        verbose_name_plural = _('comments')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_at', 'is_active']),
        ]

    def __str__(self):
        return f'{self.author.username} on {self.product} - {self.created_at:%Y-%m-%d}'

    def clean(self):
        # validation
        if len(self.body.strip()) < 2:
            raise ValidationError(
                _('Comment must contain at least 2 characters.'))

    @property
    def like_count(self):
        return self.likes.filter(is_active=True, reaction_type='like').count()

    @property
    def dislike_count(self):
        return self.likes.filter(is_active=True, reaction_type='dislike').count()

    def soft_delete(self):
        """Soft delete instead of permanent deletion"""
        self.is_active = False
        self.save()


class Like(models.Model):
    class ReactionType(models.TextChoices):
        LIKE = 'like', _('Like')
        DISLIKE = 'dislike', _('Dislike')

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='comment_likes', on_delete=models.CASCADE, verbose_name=_('user'))

    comment = models.ForeignKey(
        Comment, related_name='likes', on_delete=models.CASCADE, verbose_name=_('comment'))

    reaction_type = models.CharField(
        max_length=8, choices=ReactionType.choices, verbose_name=_('reaction type'))

    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_('created at'))

    is_active = models.BooleanField(
        default=True, verbose_name=_('active status'), help_text=_('Designates whether this like is active'))

    class Meta:
        verbose_name = _('like')
        verbose_name_plural = _('likes')
        unique_together = ('user', 'comment')
        # constraints = [...]
        indexes = [
            models.Index(fields=['user', 'comment', 'is_active']),
        ]

    def __str__(self):
        return f'{self.user.username} liked comment {self.comment.id}'

    def save(self, *args, **kwargs):
        if not self.pk:
            existing_reaction = Like.objects.filter(
                user=self.user,
                comment=self.comment,
                is_active=True,
                reaction_type=self.reaction_type,
            ).exists()
            if existing_reaction:
                raise ValidationError(
                    _('You have already reacted to this comment.'))
        super().save(*args, **kwargs)
