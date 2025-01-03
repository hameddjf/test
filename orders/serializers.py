from rest_framework import serializers

from django.core.validators import MinValueValidator, MaxValueValidator

from accounts.models import CustomUser
from orders.models import Order

from .models import Order, OrderStatusLog , Address , Payment

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
    cart_items = serializers.ListField(child=serializers.DictField(child=serializers.CharField()))
    # total_amount must be between 0 and 1000000.
    total_amount = serializers.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(1000000)])

    class Meta:
        model = Order
        fields = ['user_info', 'confirm_address', 'delivery_time',
                  'cart_items', 'total_amount']

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

        order = Order.objects.create(
            user=user,
            status='PENDING',
            delivery_time=validated_data['delivery_time'],
            total_amount=validated_data['total_amount']
        )

        cart_items = validated_data.pop('cart_items')
        for item in cart_items:
            product_id = item['product_id']
            quantity = item['quantity']
            order.addresses.add(Address.objects.get(id=product_id))
            order.save()

        return order
    
# class OrderCreateSerializer(serializers.ModelSerializer):
#     user_info = UserUpdateSerializer(write_only=True)
#     confirm_address = serializers.BooleanField(required=True)
#     delivery_time = serializers.ChoiceField(
#         choices=[
#             ('morning', 'صبح (۹ تا ۱۲)'),
#             ('afternoon', 'عصر (۱۳ تا ۱۷)'),
#             ('evening', 'شب (۱۸ تا ۲۱)')
#         ],
#         required=True
#     )
    

#     class Meta:
#         model = Order
#         fields = ['user_info', 'confirm_address', 'delivery_time']

#     def validate_confirm_address(self, value):
#         if not value:
#             raise serializers.ValidationError("لطفا آدرس را تایید کنید")
#         return value

#     def create(self, validated_data):
#         user_data = validated_data.pop('user_info')
#         user = self.context['request'].user

#         if not user.first_name and not user.last_name and not user.phone_number:
#             for attr, value in user_data.items():
#                 setattr(user, attr, value)
#             user.save()

#         # ایجاد سفارش
#         order = Order.objects.create(
#             user=user,
#             status='PENDING',
#             delivery_time=validated_data['delivery_time']
#         )

#         return order
    
    
class OrderStatusLogSerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(source='created_by.username',
                                                read_only=True)

    class Meta:
        model = OrderStatusLog
        fields = ['id', 'order', 'created_by', 'created_by_username',
                  'old_status', 'new_status', 'created_at']
        read_only_fields = ['created_by']


# class OrderSerializer(serializers.ModelSerializer):
#     status_logs = OrderStatusLogSerializer(many=True, read_only=True)
#     total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

#     class Meta:
#         model = Order
#         fields = [
#             'id', 'user', 'promotion_coupon',
#             'bank_type', 'order_number', 'status', 'is_active',
#             'created', 'updated', 'status_logs', 'total_amount'
#         ]
#         read_only_fields = ['order_number', 'status', 'bank_type']

#     def validate(self, data):
#         """
#         Custom validation to ensure that total_amount is provided.
#         """
#         if 'total_amount' not in data:
#             raise serializers.ValidationError("Total amount is required.")
#         return data

# class OrderCreateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Order
#         fields = ['cart_items', 'promotion_coupon']

#     def create(self, validated_data):
#         user = self.context['request'].user
#         validated_data['user'] = user
#         return super().create(validated_data)



class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'user', 'street_address', 'city', 'state', 'postal_code']

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['bank_record', 'order', 'tracking_code', 'amount', 'status']
        extra_kwargs = {
            'bank_record': {'required': True},
            'order': {'required': True},
            'tracking_code': {'required': True},
            'amount': {'required': True},
            'status': {'required': True},
        }