from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.db.models import Count
from django.utils import timezone
from django.utils.translation import ngettext

from .models import Comment, Like


@admin.action(description=_('activate'))
def make_active(self, request, queryset):
    updated = queryset.update(is_active=True)
    status = 'active'
    message = ngettext(
        f'{updated} comment was successfully activated.',
        f'{updated} comments were successfully activated.',
        updated
    )
    self.message_user(request, message)


@admin.action(description=_('inactivate'))
def make_inactive(self, request, queryset):
    updated = queryset.update(is_active=False)
    status = 'inactive'
    message = ngettext(
        f'{updated} comment was successfully inactivated.',
        f'{updated} comments were successfully inactivated.',
        updated
    )
    self.message_user(request, message)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'truncated_body',  # 'author_link' , 'product_link',
                    'like_count_display', 'dislike_count', 'created_at',
                    'is_active', 'status_badge')
    list_display_links = ['id', 'truncated_body']

    list_filter = ('is_active', 'created_at',
                   # ('author', admin.RelatedOnlyFieldListFilter),('product', admin.RelatedOnlyFieldListFilter),
                   )

    search_fields = ('body', 'author__username',
                     'author__email', 'product__name',)

    readonly_fields = ('created_at', 'updated_at',
                       'like_count_display', 'dislike_count',)

    fieldsets = ((_('Content'), {'fields': ('body', 'author', 'product')}),
                 (_('Metadata'), {
                  'fields': ('created_at', 'updated_at', 'is_active'), 'classes': ('collapse',)}),
                 (_('Statistics'), {
                  'fields': ('like_count_display', 'dislike_count'), 'classes': ('collapse',)}),)

    actions = [make_active, make_inactive]

    date_hierarchy = 'created_at'
    save_on_top = True

    def get_queryset(self, request):
        return super().get_queryset(request)\
            .prefetch_related('likes')\
            .prefetch_related('author')\
            .prefetch_related('product')

    @admin.display(description=_('Content'))
    def truncated_body(self, obj):
        return (obj.body[:16] + '...') if len(obj.body) > 16 else obj.body

    # @admin.display(description=_('Author'))
    # def author_link(self, obj):
    #     pass

    # @admin.display(description=_('Product'))
    # def product_link(self, obj):
    #     pass

    @admin.display(description=_('Likes'))
    def like_count_display(self, obj):
        return obj.likes.filter(is_active=True, reaction_type='like').count()

    @admin.display(description=_('Dislikes'))
    def dislike_count(self, obj):
        return obj.likes.filter(is_active=True, reaction_type='dislike').count()

    @admin.display(description=_('Status'))
    def status_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 10px; border-radius: 10px;">{}</span>',
                _('Active')
            )
        return format_html(
            '<span style="background-color: #dc3545; color: white; padding: 3px 10px; border-radius: 10px;">{}</span>',
            _('Inactive')
        )


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('id',  # 'user_link', 'comment_preview',
                    'reaction_type', 'created_at', 'is_active')
    list_display_links = ['id', 'reaction_type']

    list_filter = ('is_active', 'reaction_type', 'created_at',
                   ('user', admin.RelatedOnlyFieldListFilter),)

    search_fields = ('user__username', 'user__email', 'comment__body',)

    readonly_fields = ('created_at',)

    fieldsets = ((_('Reaction Details'), {
        'fields': ('user', 'comment', 'reaction_type')}),
        (_('Status'), {
            'fields': ('created_at', 'is_active'), 'classes': ('collapse',)}),)

    date_hierarchy = 'created_at'

    def get_queryset(self, request):
        return super().get_queryset(request)\
            .select_related('user', 'comment')

    # @admin.display(description=_('User'))
    # def user_link(self, obj):
        # pass

    # @admin.display(description=_('Comment'))
    # def comment_preview(self, obj):
        # pass


# better showing
admin.site.site_header = _('Comment Management System')
# admin.site.site_title
# admin.site.index_title
