# Generated by Django 4.2.7 on 2024-12-21 16:43

import carts.validators
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('products', '__first__'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Promotion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('discount_type', models.CharField(choices=[('PRODUCT', 'تخفیف محصول'), ('COUPON', 'کد تخفیف')], max_length=10)),
                ('discount_percent', models.IntegerField(validators=[carts.validators.validate_discount_percent, django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('code', models.CharField(blank=True, max_length=30, null=True, unique=True, validators=[carts.validators.validate_promotion_code])),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField(validators=[carts.validators.validate_future_date])),
                ('is_active', models.BooleanField(default=True)),
                ('max_uses', models.PositiveIntegerField(blank=True, default=1, null=True, validators=[carts.validators.validate_positive_number])),
                ('used_count', models.PositiveIntegerField(default=0)),
                ('products', models.ManyToManyField(blank=True, to='products.product')),
            ],
        ),
        migrations.CreateModel(
            name='CartItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1, validators=[carts.validators.validate_positive_number, django.core.validators.MinValueValidator(1)])),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('coupon', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cart_items', to='carts.promotion')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cart_items', to='products.product')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cart_items', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
                'indexes': [models.Index(fields=['user', 'is_active'], name='carts_carti_user_id_94e2be_idx'), models.Index(fields=['product', 'is_active'], name='carts_carti_product_da3891_idx')],
            },
        ),
    ]
