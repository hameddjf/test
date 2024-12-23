# Generated by Django 4.2.7 on 2024-12-21 16:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('azbankgateways', '0005_alter_bank_bank_type_alter_bank_created_at_and_more'),
        ('carts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('street_address', models.CharField(max_length=255)),
                ('city', models.CharField(max_length=100)),
                ('state', models.CharField(max_length=100)),
                ('postal_code', models.CharField(max_length=20)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='addresses', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bank_type', models.CharField(choices=[('ZARINPAL', 'zarinpal'), ('IDPAY', 'idpay')], max_length=8, null=True)),
                ('order_number', models.CharField(max_length=32, unique=True)),
                ('status', models.CharField(choices=[('PENDING', 'pending'), ('PROCESSING', 'processing'), ('PAID', 'paid'), ('SHIPPED', 'shipped'), ('DELIVERED', 'delivered'), ('CANCELLED', 'cancelled')], db_index=True, default='PENDING', max_length=16)),
                ('is_active', models.BooleanField(db_index=True, default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('addresses', models.ManyToManyField(blank=True, related_name='orders', to='orders.address')),
                ('bank_record', models.OneToOneField(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='azbankgateways.bank')),
                ('cart_items', models.ManyToManyField(related_name='orders', to='carts.cartitem')),
                ('promotion_coupon', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to='carts.promotion')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created'],
                'permissions': [('can_cancel_order', 'Can cancel order'), ('can_process_order', 'Can process order')],
            },
        ),
        migrations.CreateModel(
            name='OrderStatusLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('old_status', models.CharField(choices=[('PENDING', 'pending'), ('PROCESSING', 'processing'), ('PAID', 'paid'), ('SHIPPED', 'shipped'), ('DELIVERED', 'delivered'), ('CANCELLED', 'cancelled')], max_length=16)),
                ('new_status', models.CharField(choices=[('PENDING', 'pending'), ('PROCESSING', 'processing'), ('PAID', 'paid'), ('SHIPPED', 'shipped'), ('DELIVERED', 'delivered'), ('CANCELLED', 'cancelled')], max_length=16)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='status_logs', to='orders.order')),
            ],
            options={
                'verbose_name': 'Order Status Log',
                'verbose_name_plural': 'Order Status Logs',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['status', 'is_active'], name='orders_orde_status_089961_idx'),
        ),
    ]
