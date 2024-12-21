from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.urls import reverse

# Create your models here.


User = get_user_model()


class Blog(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(verbose_name="توضیحات")
    poster = models.ImageField(upload_to='blog/images/')
    user = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.CASCADE,
        related_name='user_blogs',
    )
    publish = models.BooleanField(default=True)
    slug = models.SlugField(unique=True, blank=True)
    created = models.DateTimeField(
        auto_now_add=True)
    updated = models.DateTimeField(
        auto_now=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)
