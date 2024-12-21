from decimal import Decimal
from typing import List, Dict

from django.core.cache import cache

from .models import CartItem, Promotion


def format_price(value):
    if value is None:
        return ''

    value = str(int(value))

    parts = []
    while value:
        parts.insert(0, value[-3:])
        value = value[:-3]

    formatted_value = ','.join(parts)

    # Convert English numbers to Farsi
    persian_numbers = formatted_value.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹')
    formatted_value = formatted_value.translate(persian_numbers)

    return f"{formatted_value} تومان"


def calculate_cart_totals(cart_items: List[CartItem]) -> Dict:
    """Calculate cart totals including subtotal, discount and final total"""

    # if cart is empty
    if not cart_items:
        return {
            'subtotal': 0,
            'total_discount': 0,
            'final_total': 0,
            'items_count': 0,
            'total_quantity': 0
        }

    # if cart is not empty
    user_id = cart_items[0].user.id
    cache_key = f'cart_totals_{user_id}'
    cached_result = cache.get(cache_key)

    if cached_result:
        return cached_result

    subtotal = sum(item.get_subtotal() for item in cart_items)
    final_total = sum(item.calculate_final_price() for item in cart_items)
    total_discount = subtotal - final_total

    result = {
        'subtotal': subtotal,
        'total_discount': total_discount,
        'final_total': final_total,
        'items_count': len(cart_items),
        'total_quantity': sum(item.quantity for item in cart_items)
    }
    # Save in cache for 5 minutes
    cache.set(cache_key, result, 300)
    return result


def validate_promotion_code(code: str, user_id: int) -> Dict:
    """Validate promotion code and return promotion details"""
    cache_key = f'promotion_validation_{code}_{user_id}'
    cached_result = cache.get(cache_key)

    if cached_result:
        return cached_result

    try:
        promotion = Promotion.objects.get(
            code=code,
            is_active=True
        )

        result = {
            'is_valid': promotion.is_valid(),
            'discount_type': promotion.discount_type,
            'discount_value': promotion.discount_percent,
            'message': 'Discount code is valid' if promotion.is_valid() else 'Discount code has expired'
        }

        cache.set(cache_key, result, 300)
        return result

    except Promotion.DoesNotExist:
        return {
            'is_valid': False,
            'message': 'The discount code is invalid'
        }
