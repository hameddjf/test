from django.contrib import admin

from .models import Promotion
# Register your models here.


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ['title', 'discount_type', 'discount_percent', 'code',
                    'start_date', 'end_date', 'is_active', 'used_count']
    list_filter = ['discount_type', 'is_active', 'start_date', 'end_date']
    search_fields = ['title', 'code']
    filter_horizontal = ['products']
    readonly_fields = ['used_count']

    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('title', 'discount_type', 'discount_percent')
        }),
        ('تنظیمات کد تخفیف', {
            'fields': ('code', 'products')
        }),
        ('زمان‌بندی', {
            'fields': ('start_date', 'end_date', 'is_active')
        }),
        ('محدودیت استفاده', {
            'fields': ('max_uses', 'used_count')
        }),
    )


# @admin.register(CartItem)
# class CartItemAdmin(admin.ModelAdmin):
#     list_display = ['user', 'product', 'quantity', 'is_active', 'created_at',
#                     'get_final_price']
#     list_filter = ['is_active', 'created_at']
#     search_fields = ['user__username', 'product__title']
#     raw_id_fields = ['user', 'product', 'coupon']
#     readonly_fields = ['created_at', 'updated_at']

#     fieldsets = (
#         ('اطلاعات کاربر', {
#             'fields': ('user', 'is_active')
#         }),
#         ('اطلاعات محصول', {
#             'fields': ('product', 'quantity')
#         }),
#         ('تخفیف', {
#             'fields': ('coupon',)
#         }),
#         ('زمان', {
#             'fields': ('created_at', 'updated_at')
#         }),
#     )

#     @admin.display(description='قیمت نهایی')
#     def get_final_price(self, obj):
#         return format_price(obj.calculate_final_price())
