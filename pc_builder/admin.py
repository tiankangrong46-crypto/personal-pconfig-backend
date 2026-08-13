from django.contrib import admin

from .models import Component


@admin.register(Component)
class ComponentAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "is_active", "sort_order", "updated_at")
    list_filter = ("category", "is_active")
    search_fields = ("name",)
    list_editable = ("is_active", "sort_order")
    ordering = ("category", "sort_order", "name")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("基本信息", {"fields": ("category", "name", "is_active", "sort_order")} ),
        ("兼容信息", {"fields": ("attributes",), "description": "JSON 格式，例如：{\"socket\": \"AM5\", \"ddr\": [\"DDR5\"]}"}),
        ("时间", {"fields": ("created_at", "updated_at")}),
    )
