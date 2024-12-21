from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from .models import Order, OrderStatusLog, Status , OrderStatusManager , Address
# Register your models here.

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'street_address', 'city', 'state', 'postal_code']
    list_filter = ['user', 'city', 'state', 'postal_code']
    search_fields = ['street_address', 'city', 'state', 'postal_code']
    readonly_fields = ['user']

    def has_add_permission(self, request):
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

@admin.register(OrderStatusLog)
class OrderStatusLogAdmin(admin.ModelAdmin):
    list_display = ['order_number',
                    'status_change', 'created_by', 'created_at']
    list_filter = ['old_status', 'new_status', 'created_at']
    search_fields = ['order__order_number', 'created_by__username']
    readonly_fields = ['old_status',
                       'new_status', 'created_by', 'created_at']
    save_on_top = True

    def order_number(self, obj):
        return obj.order.order_number
    order_number.short_description = _('Order Number')

    def status_change(self, obj):
        return format_html(
            '<span style="color: #666;">{}</span> → <span style="color: #000;">{}</span>',
            obj.get_old_status_display(),
            obj.get_new_status_display()
        )
    status_change.short_description = _('Status Change')


class OrderStatusLogInline(admin.TabularInline):
    model = OrderStatusLog
    extra = 0
    readonly_fields = ['old_status', 'new_status', 'created_by', 'created_at']
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.action(description=_('Cancel selected orders'))
def cancel_orders(self, request, queryset):
    for order in queryset:
        try:
            OrderStatusManager(order).cancel()
        except ValidationError:
            self.message_user(request,
                              f'Could not cancel order {order.order_number}', level='ERROR')


@admin.action(description=_('Process selected orders'))
def process_orders(self, request, queryset):
    for order in queryset:
        try:
            OrderStatusManager(order).process()
        except ValidationError:
            self.message_user(request,
                              f'Could not process order {
                                  order.order_number}',
                              level='ERROR')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user_link', 'status_badge', 'total_items',
                    'bank_type', 'created', 'is_active']
    list_filter = ['status', 'is_active', 'bank_type', 'created']
    search_fields = ['order_number', 'user__username', 'user__email']
    readonly_fields = ['order_number', 'created', 'updated']
    inlines = [OrderStatusLogInline]
    save_on_top = True
    actions = [cancel_orders, process_orders]

    fieldsets = (
        (_('Basic Information'), {
            'fields': ('order_number', 'user', 'status', 'is_active')
        }),
        (_('Payment Details'), {
            'fields': ('bank_type', 'bank_record', 'promotion_coupon')
        }),
        (_('Items'), {
            'fields': ('cart_items', 'addresses')
        }),
        (_('Timestamps'), {
            'fields': ('created', 'updated'),
            'classes': ('collapse',)
        })
    )

    def user_link(self, obj):
        url = reverse('admin:accounts_customuser_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    user_link.short_description = _('User')

    def status_badge(self, obj):
        colors = {
            'PENDING': '#ffa500',
            'PAID': '#28a745',
            'PROCESSING': '#17a2b8',
            'SHIPPED': '#007bff',
            'DELIVERED': '#28a745',
            'CANCELLED': '#dc3545'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px;">{}</span>',
            colors.get(obj.status, '#666'),
            obj.get_status_display()
        )
    status_badge.short_description = _('Status')

    def total_items(self, obj):
        return obj.cart_items.count()
    total_items.short_description = _('Total Items')

    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.status in [Status.DELIVERED, Status.CANCELLED]:
            return self.readonly_fields + ['status', 'cart_items', 'bank_type',
                                           'bank_record', 'promotion_coupon']
        return self.readonly_fields

    def has_delete_permission(self, request, obj=None):
        if obj and obj.status not in [Status.PENDING, Status.CANCELLED]:
            return False
        return super().has_delete_permission(request, obj)

    actions = ['cancel_orders', 'process_orders']

    def get_actions(self, request):
        actions = super().get_actions(request)
        if not request.user.has_perm('order.can_cancel_order'):
            actions.pop('cancel_orders', None)
        if not request.user.has_perm('order.can_process_order'):
            actions.pop('process_orders', None)
        return actions
