from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

from .validators import (
    validate_future_date,
    validate_positive_number,
    validate_discount_percent,
    validate_promotion_code
)

# Create your models here.


class Promotion(models.Model):
    PROMOTION_TYPES = [
        ('PRODUCT', 'تخفیف محصول'),
        ('COUPON', 'کد تخفیف'),
    ]

    title = models.CharField(max_length=100)
    discount_type = models.CharField(max_length=10, choices=PROMOTION_TYPES)
    discount_percent = models.IntegerField(validators=[validate_discount_percent, MinValueValidator(0), MaxValueValidator(100)])

    code = models.CharField(max_length=30, blank=True, null=True,unique=True, validators=[validate_promotion_code])

    products = models.ManyToManyField('products.Product', blank=True)

    start_date = models.DateTimeField()
    end_date = models.DateTimeField(validators=[validate_future_date])
    is_active = models.BooleanField(default=True)

    max_uses = models.PositiveIntegerField(
        default=1, blank=True, null=True, validators=[validate_positive_number])
    used_count = models.PositiveIntegerField(default=0)

    def calculate_discount_amount(self, base_price: int) -> int:
        """Calculation of discount amount"""
        return (base_price * self.discount_percent) // 100

    def is_valid(self) -> bool:
        now = timezone.now()
        return (
            self.is_active and
            self.start_date <= now <= self.end_date and
            (self.max_uses is None or self.used_count < self.max_uses)
        )


# class CartItem(models.Model):
#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart_items')

#     product = models.ForeignKey(
#         'products.Product', on_delete=models.CASCADE, related_name='cart_items')

#     coupon = models.ForeignKey(
#         Promotion, on_delete=models.SET_NULL,
#         null=True, blank=True, related_name='cart_items')

#     quantity = models.PositiveIntegerField(
#         default=1, validators=[validate_positive_number, MinValueValidator(1)])
#     is_active = models.BooleanField(default=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         ordering = ['-created_at']
#         indexes = [
#             models.Index(fields=['user', 'is_active']),
#             models.Index(fields=['product', 'is_active']),
#         ]

#     def get_product_price_with_promotion(self) -> int:
#         """Calculating the base price of the product including the product discount"""
#         base_price = self.product.price

#         product_promotion = Promotion.objects.filter(
#             discount_type='PRODUCT',
#             products=self.product,
#             is_active=True,
#             start_date__lte=timezone.now(),
#             end_date__gte=timezone.now()
#         ).order_by('-discount_percent').first()

#         if product_promotion and product_promotion.is_valid():
#             base_price -= product_promotion.calculate_discount_amount(
#                 base_price)

#         return max(0, int(base_price))

#     def get_subtotal(self) -> int:
#         """Calculation of total price by quantity (without coupon)"""
#         unit_price = self.get_product_price_with_promotion()
#         return unit_price * self.quantity

#     def calculate_final_price(self) -> int:
#         """Calculating the final price including all discounts"""
#         subtotal = self.get_subtotal()

#         # apply coupon (if coupon entered)
#         if self.coupon and self.coupon.is_valid():
#             subtotal -= self.coupon.calculate_discount_amount(subtotal)

#         return max(0, subtotal)

#     # def get_total_discount(self) -> Decimal:
#     #     """Calculation of the total discount applied"""
#     #     original_price = self.product.price * self.quantity
#     #     final_price = self.calculate_final_price()
#     #     return (original_price - final_price).quantize(Decimal('0.01'))

#     def clean(self):
#         super().clean()
#         if self.quantity > self.product.stock:
#             raise ValidationError({
#                 'quantity': _("Quantity cannot exceed available stock.")
#             })
#         if self.coupon and self.coupon.discount_type != 'COUPON':
#             raise ValidationError({
#                 'coupon': _("Invalid coupon type.")
#             })

#     def save(self, *args, **kwargs):
#         self.full_clean()
#         super().save(*args, **kwargs)

#     def __str__(self):
#         return f"{self.user.username} - {self.product.title} ({self.quantity})"
