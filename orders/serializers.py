from rest_framework import serializers

from carts.serializers import CartItemSerializer
from accounts.models import CustomUser
from orders.models import Order

from .models import Order, OrderStatusLog , Address

# serializers.py

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'phone_number']

class OrderCreateSerializer(serializers.ModelSerializer):
    user_info = UserUpdateSerializer(write_only=True)
    confirm_address = serializers.BooleanField(required=True)
    delivery_time = serializers.ChoiceField(
        choices=[
            ('morning', 'صبح (۹ تا ۱۲)'),
            ('afternoon', 'عصر (۱۳ تا ۱۷)'),
            ('evening', 'شب (۱۸ تا ۲۱)')
        ],
        required=True
    )

    class Meta:
        model = Order
        fields = ['user_info', 'confirm_address', 'delivery_time']

    def validate_confirm_address(self, value):
        if not value:
            raise serializers.ValidationError("لطفا آدرس را تایید کنید")
        return value

    def create(self, validated_data):
        user_data = validated_data.pop('user_info')
        user = self.context['request'].user

        if not user.first_name and not user.last_name and not user.phone_number:
            for attr, value in user_data.items():
                setattr(user, attr, value)
            user.save()

        # ایجاد سفارش
        order = Order.objects.create(
            user=user,
            status='PENDING',
            delivery_time=validated_data['delivery_time']
        )

        return order
    
    
class OrderStatusLogSerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(source='created_by.username',
                                                read_only=True)

    class Meta:
        model = OrderStatusLog
        fields = ['id', 'order', 'created_by', 'created_by_username',
                  'old_status', 'new_status', 'created_at']
        read_only_fields = ['created_by']


class OrderSerializer(serializers.ModelSerializer):
    cart_items = CartItemSerializer(many=True, read_only=True)
    status_logs = OrderStatusLogSerializer(many=True, read_only=True)
    total_amount = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'user', 'cart_items', 'promotion_coupon',
                  'bank_type', 'order_number', 'status', 'is_active',
                  'created', 'updated', 'status_logs', 'total_amount']
        read_only_fields = ['order_number', 'status', 'bank_type']

    def get_total_amount(self, obj):
        return sum(item.calculate_final_price() for item in obj.cart_items.all())


class OrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['cart_items', 'promotion_coupon']

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)



class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'user', 'street_address', 'city', 'state', 'postal_code']
