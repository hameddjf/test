from azbankgateways.models import Bank
import logging

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.db import transaction
from django.utils.translation import gettext as _
from django.core.exceptions import ValidationError

from .models import Order, OrderStatusLog , OrderStatusManager


# Signal to update order status after successful payment
@receiver(post_save, sender=Bank)
def handle_successful_payment(sender, instance, **kwargs):
    try:
        with transaction.atomic():
            order = instance.order
            order_manager = OrderStatusManager(order)
            order_manager.process_payment(order.bank_type)

            for item in order.cart_items.all():
                product = item.product
                if product.stock >= item.quantity:
                    product.stock -= item.quantity
                    product.save()

                    # Deactivate product if stock reaches 0
                    if product.stock == 0:
                        product.active = False
                        product.save()
                else:
                    raise ValueError(
                        f"Insufficient stock for product {product.id}.")

            # Deactivate all cart items
            order.cart_items.update(active=False)

            logging.info(
                f"Order {order.order_number} payment processed successfully.")

    except Exception as e:
        logging.error(f"Error in handle_successful_payment: {str(e)}")


# Signal to record order status changes
@receiver(pre_save, sender=Order)
def log_status_change(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_order = Order.objects.get(pk=instance.pk)
            if old_order.status != instance.status:
                OrderStatusLog.objects.create(
                    order=instance,
                    old_status=old_order.status,
                    new_status=instance.status
                )
                logging.info(
                    f"Order {instance.order_number} status changed from {old_order.status} to {instance.status}")
        except Order.DoesNotExist:
            pass


# Signal to validate order when created
@receiver(post_save, sender=Order)
def validate_new_order(sender, instance, created, **kwargs):
    if created:
        try:
            # بررسی موجودی محصولات
            for item in instance.cart_items.all():
                if item.quantity > item.product.stock:
                    raise ValidationError(
                        _(f"Insufficient stock for product {item.product.id}")
                    )
            logging.info(
                f"New order {instance.order_number} validated successfully")
        except Exception as e:
            logging.error(f"Error in validate_new_order: {str(e)}")
