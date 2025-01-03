# Generated by Django 4.2.7 on 2024-12-21 16:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import imagekit.models.fields
import mptt.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Name')),
                ('slug', models.SlugField(unique=True, verbose_name='Slug')),
                ('statuses', models.BooleanField(default=True, verbose_name='آیا نمایش داده شود؟')),
                ('lft', models.PositiveIntegerField(editable=False)),
                ('rght', models.PositiveIntegerField(editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(editable=False)),
                ('parent', mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='products.category')),
            ],
            options={
                'verbose_name': 'Category',
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.CreateModel(
            name='IpAddress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip_address', models.GenericIPAddressField(verbose_name='آدرس آیپی')),
            ],
        ),
        migrations.CreateModel(
            name='MostViewed',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('ip', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.ipaddress')),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50)),
                ('slug', models.SlugField(unique=True)),
                ('color', models.CharField(choices=[('blue', 'blue'), ('red', 'red'), ('white', 'white'), ('brown', 'brown')], max_length=50)),
                ('size', models.CharField(choices=[('LARGE', 'LARGE'), ('MEDIUM', 'MEDIUM'), ('XLARGE', 'XLARGE'), ('XXLARGE', 'XXLARGE')], max_length=50)),
                ('price', models.IntegerField()),
                ('stock', models.IntegerField(default=0)),
                ('sold', models.IntegerField(default=0)),
                ('description', models.TextField(blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('active', models.BooleanField(default=False)),
                ('poster', models.ImageField(upload_to='poster/')),
                ('category', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='products.category', verbose_name='Category')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='user')),
                ('view_count', models.ManyToManyField(blank=True, related_name='hits', through='products.MostViewed', to='products.ipaddress', verbose_name='بازدیدها')),
            ],
            options={
                'verbose_name': 'Product',
                'verbose_name_plural': 'Products',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='ProductGallery',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('original_images', models.ImageField(upload_to='original_images/')),
                ('resizes_images', imagekit.models.fields.ProcessedImageField(blank=True, null=True, upload_to='resizes_images/')),
                ('product', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='products.product')),
            ],
            options={
                'verbose_name': 'Gallery',
                'verbose_name_plural': 'Galleries',
                'ordering': ['product'],
            },
        ),
        migrations.AddField(
            model_name='mostviewed',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.product'),
        ),
        migrations.AddField(
            model_name='mostviewed',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
