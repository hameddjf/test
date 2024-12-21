# Generated by Django 4.2.7 on 2024-12-21 16:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('blogs', '0001_initial'),
        ('products', '__first__'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('body', models.TextField(help_text='The content of the comment', max_length=1000, verbose_name='comment text')),
                ('created_at', models.DateTimeField(db_index=True, default=django.utils.timezone.now, verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated at')),
                ('is_active', models.BooleanField(default=True, help_text='comment is active or soft deleted', verbose_name='active status')),
                ('author', models.ForeignKey(help_text='User who wrote the comment', on_delete=django.db.models.deletion.CASCADE, related_name='product_comments', to=settings.AUTH_USER_MODEL, verbose_name='author')),
                ('blog', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='blogs.blog')),
                ('product', models.ForeignKey(help_text='The product this comment belongs to', on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='products.product', verbose_name='product')),
            ],
            options={
                'verbose_name': 'comment',
                'verbose_name_plural': 'comments',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Like',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reaction_type', models.CharField(choices=[('like', 'Like'), ('dislike', 'Dislike')], max_length=8, verbose_name='reaction type')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this like is active', verbose_name='active status')),
                ('comment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='likes', to='comments.comment', verbose_name='comment')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comment_likes', to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
            options={
                'verbose_name': 'like',
                'verbose_name_plural': 'likes',
                'indexes': [models.Index(fields=['user', 'comment', 'is_active'], name='comments_li_user_id_976425_idx')],
                'unique_together': {('user', 'comment')},
            },
        ),
        migrations.AddIndex(
            model_name='comment',
            index=models.Index(fields=['created_at', 'is_active'], name='comments_co_created_6a3967_idx'),
        ),
    ]
