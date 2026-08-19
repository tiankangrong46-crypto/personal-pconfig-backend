from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
import json
from django.urls import path

from .models import Component
from .importers import parse_upload, normalize_component_record, import_records


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

    def get_urls(self):
        return [path("import/", self.admin_site.admin_view(self.import_view), name="pc_builder_component_import")] + super().get_urls()

    @staff_member_required
    def import_view(self, request):
        context = {**self.admin_site.each_context(request), "title": "批量导入组件"}
        if request.method == "POST" and request.FILES.get("file"):
            try:
                records = json.loads(request.POST["records"]) if request.POST.get("confirm") == "true" and request.POST.get("records") else parse_upload(request.FILES["file"])
                if request.POST.get("confirm") == "true":
                    context["result"] = import_records(records)
                else:
                    errors, preview = [], []
                    for row, record in enumerate(records, 1):
                        try: preview.append(normalize_component_record(record))
                        except ValueError as exc: errors.append({"row": row, "message": str(exc)})
                    context.update({"preview": preview, "errors": errors, "records_json": json.dumps(records, ensure_ascii=False)})
            except ValueError as exc:
                context["errors"] = [{"row": 0, "message": str(exc)}]
        return render(request, "admin/pc_builder/component/import.html", context)
