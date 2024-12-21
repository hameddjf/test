from rest_framework import serializers
from .models import Rating
from products.models import Product


class RatingSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    product_name = serializers.SerializerMethodField()

    class Meta:
        model = Rating
        fields = ['id', 'score', 'product',
                  'product_name', 'user', 'created_at']
        read_only_fields = ['user', 'product_name']

    def get_product_name(self, obj):
        return obj.product.name if obj.product else None

    def validate(self, data):
        request = self.context['request']
        product = data.get('product')

        # چک کردن تکراری نبودن امتیاز
        existing_rating = Rating.objects.filter(
            user=request.user,
            product=product
        ).exists()

        if existing_rating and self.instance is None:  # در حالت create
            raise serializers.ValidationError(
                "شما قبلاً به این محصول امتیاز داده‌اید")

        # اعتبارسنجی امتیاز
        if not (1 <= data['score'] <= 5):
            raise serializers.ValidationError("امتیاز باید بین 1 تا 5 باشد")

        return data
