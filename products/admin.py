from mptt.admin import DraggableMPTTAdmin
from django.db import models
from django.utils.translation import ngettext
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.db.models import Count

from .models import Category, Product, ProductGallery, IpAddress, MostViewed

# Register your models here.


@admin.action(description=_('activate'))
def make_active(self, request, queryset):
    updated = queryset.update(statuses=True)
    status = 'active'
    message = ngettext(
        f'{updated} category was successfully marked as {status}.',
        f'{updated} categories were successfully marked as {status}.',
        updated
    )
    self.message_user(request, message)


@admin.action(description=_('inactivate'))
def make_inactive(self, request, queryset):
    updated = queryset.update(statuses=False)
    status = 'inactive'
    message = ngettext(
        f'{updated}  successfully marked as {status}.',
        f'{updated}  successfully marked as {status}.',
        updated
    )
    self.message_user(request, message)


@admin.register(Category)
class CategoryAdmin(DraggableMPTTAdmin):
    list_display = ('tree_actions', 'name', 'parent',
                    'status_display', 'get_tree_level')
    list_display_links = ('name', 'parent')

    list_filter = ('statuses', 'parent')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    actions = [make_active, make_inactive]

    save_on_top = True

    def status_display(self, obj):
        return format_html(
            '<span style="color: {};">{}</span>',
            'green' if obj.statuses else 'red',
            '✓' if obj.statuses else '✗'
        )
    status_display.short_description = _('Status')
    status_display.admin_order_field = 'statuses'

    def get_tree_level(self, obj):
        return format_html(
            '{}{}',
            '—' * obj.level,
            obj.name
        )
    get_tree_level.short_description = _('Tree Structure')

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


class ProductGalleryInline(admin.TabularInline):
    model = ProductGallery
    extra = 1
    readonly_fields = ('preview_image',)
    fields = ('original_images', 'preview_image')

    def preview_image(self, obj):
        if obj.resizes_images:
            return format_html(
                '<img src="{}" style="max-width:100px;max-height:100px;"/>',
                obj.resizes_images.url
            )
        return "No image"
    preview_image.short_description = _('Preview')

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id','title', 'image_thumbnail', 'category', 'price',
                    'stock_status', 'active_status', 'created')
    list_filter = ('active', 'category', 'color', 'size')
    search_fields = ('title', 'description', 'category__name')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created', 'updated', 'sold', 'view_count_display')
    actions = [make_active, make_inactive]

    date_hierarchy = 'created'
    save_on_top = True

    inlines = [ProductGalleryInline]

    fieldsets = (
        (_('Basic Information'), {
            'fields': (('title', 'slug'), ('user', 'category'), 'description')}),
        (_('Product Details'), {
            'fields': (('color', 'size'), ('price', 'stock', 'sold'))}),
        (_('Media'), {
            'fields': ('poster', )}),
        (_('Status and Statistics'), {
            'fields': (('active', 'view_count_display'), ('created', 'updated')), 'classes': ('collapse',)}),
    )

    def view_count_display(self, obj):
        count = obj.view_count.count()
        return f"{count} view{'s' if count != 1 else ''}"
    view_count_display.short_description = _('View Count')

    def stock_status(self, obj):
        if obj.stock > 10:
            color = 'green'
            text = f'In Stock ({obj.stock})'
        elif 0 < obj.stock <= 10:
            color = 'orange'
            text = f'Low Stock ({obj.stock})'
        else:
            color = 'red'
            text = 'Out of Stock'
        return format_html('<span style="color: {};">{}</span>', color, text)
    stock_status.short_description = _('Stock Status')

    def active_status(self, obj):
        return format_html(
            '<img src="/static/admin/img/icon-{}.svg" alt="{}">',
            'yes' if obj.active else 'no',
            'Active' if obj.active else 'Inactive'
        )
    active_status.short_description = _('Active')

    @admin.display(description=_('Thumbnail'))
    def image_thumbnail(self, obj):
        if obj.poster:
            return format_html(
                '<img src="{}" style="width:50px;height:50px;object-fit:cover;"/>',
                obj.poster.url
            )
        return "-"

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


@admin.register(ProductGallery)
class ProductGalleryAdmin(admin.ModelAdmin):
    list_display = ('get_product_title', 'image_preview', 'resized_preview')
    list_select_related = ['product']
    search_fields = ('product__title',)

    def get_product_title(self, obj):
        return obj.product.title
    get_product_title.short_description = _('Product')
    get_product_title.admin_order_field = 'product__title'

    @admin.display(description=_('Original'))
    def image_preview(self, obj):
        return self._get_image_preview(obj.original_images)

    @admin.display(description=_('Resized'))
    def resized_preview(self, obj):
        return self._get_image_preview(obj.resizes_images)

    def _get_image_preview(self, image):
        if image:
            return format_html(
                '<img src="{}" style="width:80px;height:80px;object-fit:cover;"/>',
                image.url
            )
        return "-"

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


@admin.register(IpAddress)
class IpAddressAdmin(admin.ModelAdmin):
    list_display = ('ip_address', 'views_count', 'last_view_date')
    search_fields = ('ip_address',)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            _views_count=Count('mostviewed'),
            _last_view=models.Max('mostviewed__created')
        )

    @admin.display(ordering='_views_count', description=_('Views Count'))
    def views_count(self, obj):
        return obj._views_count

    @admin.display(ordering='_last_view', description=_('Last View'))
    def last_view_date(self, obj):
        return obj._last_view

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


@admin.register(MostViewed)
class MostViewedAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'ip_address_display', 'created_display')
    list_filter = ('created', 'product', 'user')
    search_fields = ('product__title', 'user__username', 'ip__ip_address')
    list_select_related = ['product', 'user', 'ip']
    date_hierarchy = 'created'

    def ip_address_display(self, obj):
        return obj.ip.ip_address
    ip_address_display.short_description = _('IP Address')

    def created_display(self, obj):
        return obj.created.strftime('%Y-%m-%d %H:%M:%S')
    created_display.short_description = _('Created At')
    created_display.admin_order_field = 'created'

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions
