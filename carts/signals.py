from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.cache import cache

from .models import Promotion


# @receiver([post_save, post_delete], sender=CartItem)
# def update_product_stock(sender, instance, **kwargs):
#     """Update product stock when cart item is modified"""
#     product = instance.product
#     # clear cache
#     cache_key = f'product_stock_{product.id}'
#     cache.delete(cache_key)

#     if kwargs.get('created', False):
#         product.stock -= instance.quantity
#     elif kwargs.get('signal') == post_delete:
#         product.stock += instance.quantity
#     product.save()


# @receiver(pre_save, sender=CartItem)
# def check_product_stock(sender, instance, **kwargs):
#     validate_positive_number(instance.quantity)
#     if instance.pk is None:
#         current_stock = instance.product.stock
#         if instance.quantity > current_stock:
#             raise ValidationError(
#                 f"Insufficient inventory. Current inventory: {current_stock}"
#             )


@receiver(post_save, sender=Promotion)
def clear_promotion_cache(sender, instance, **kwargs):
    """Clear promotion cache when a promotion is modified"""
    cache_key = f'promotion_{instance.code}'
    cache.delete(cache_key)
