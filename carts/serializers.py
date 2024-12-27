from rest_framework import serializers

from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from .models import Promotion


class PromotionSerializer(serializers.ModelSerializer):
    time_remaining = serializers.SerializerMethodField()

    class Meta:
        model = Promotion
        fields = [
            'id', 'title', 'discount_type', 'discount_percent',
            'code', 'products', 'start_date', 'end_date',
            'is_active', 'max_uses', 'used_count', 'time_remaining'
        ]
        read_only_fields = ['used_count']
        
    def get_time_remaining(self, obj):
        now = timezone.now()
        if obj.end_date > now:
            remaining_time = obj.end_date - now
            days = remaining_time.days
            hours, remainder = divmod(remaining_time.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            return {
                'days': days,
                'hours': hours,
                'minutes': minutes,
                'seconds': seconds
            }
        return {
            'days': 0,
            'hours': 0,
            'minutes': 0,
            'seconds': 0
        }

    def get_days_remaining(self, obj):
        from django.utils import timezone
        if obj.end_date > timezone.now():
            return (obj.end_date - timezone.now()).days
        return 0

    def validate(self, data):
        if data.get('start_date') and data.get('end_date'):
            if data['start_date'] >= data['end_date']:
                raise serializers.ValidationError(
                    "The end date must be after the start date"
                )
        if data.get('discount_type') == 'COUPON' and not data.get('code'):
            raise serializers.ValidationError(
                "Discount code is required for coupon type"
            )
        return data


# class CartItemSerializer(serializers.ModelSerializer):
#     product_title = serializers.CharField(
#         source='product.title', read_only=True)
#     final_price = serializers.IntegerField(
#         source='calculate_final_price',
#         read_only=True)
#     product_price = serializers.IntegerField(
#         source='get_product_price_with_promotion',
#         read_only=True)
#     subtotal = serializers.IntegerField(
#         source='get_subtotal',
#         read_only=True)

#     class Meta:
#         model = CartItem
#         fields = [
#             'id', 'user', 'product', 'product_title',
#             'coupon', 'quantity', 'is_active',
#             'product_price', 'subtotal', 'final_price',
#             'created_at'
#         ]
#         read_only_fields = ['user', 'created_at']

#     def validate_quantity(self, value):
#         validate_positive_number(value)
#         if value < 1:
#             raise serializers.ValidationError(
#                 "Number must be at least 1"
#             )
#         return value

#     def validate(self, data):
#         if data.get('quantity') and data.get('product'):
#             if data['quantity'] > data['product'].stock:
#                 raise serializers.ValidationError(
#                     "Quantity requested is more than stock"
#                 )
#         return data
