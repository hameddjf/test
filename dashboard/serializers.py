from rest_framework import serializers

from accounts.models import CustomUser
from orders.models import Order

class OrderHistorySerializer(serializers.ModelSerializer):
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, source='get_total_amount')
    items_count = serializers.IntegerField(source='cart_items.count')

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'status', 
            'created', 'total_amount', 'items_count'
        ]

    def get_total_amount(self, obj):
        return sum(item.calculate_final_price() for item in obj.cart_items.all())

    def get_items_count(self, obj):
        return obj.cart_items.count()
    
class UserProfileSerializer(serializers.ModelSerializer):
    order_stats = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            'id', 'first_name', 'last_name', 'email', 
            'username','order_stats'
        ]
    def get_order_stats(self, obj):
        orders = Order.objects.filter(user=obj)
        return {
            'total_orders': orders.count(),
            'pending_orders': orders.filter(status='PENDING').count(),
            'completed_orders': orders.filter(status='COMPLETED').count()
        }
