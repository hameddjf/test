from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import Blog

# Register your models here.


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'publish', 'show_image', 'created']
    list_filter = ['publish', 'created', 'updated']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('user',)
    list_editable = ['publish']
    list_per_page = 20

    @admin.display(description=_('image'))
    def show_image(self, obj):
        if obj.poster:
            return format_html(f'<img src="{obj.poster.url}" width="50" height="50" />')
        return format_html('<p>No image</p>')
