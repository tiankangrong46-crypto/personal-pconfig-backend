import json
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.views.decorators.http import require_http_methods

from .models import Component
from .importers import import_records, parse_upload, normalize_component_record


@require_GET
def component_list(request):
    category = request.GET.get("category")
    components = Component.objects.filter(is_active=True)
    if category:
        category = category.strip().lower()
        components = components.filter(category=category)

    data = [
        {
            "id": component.id,
            "category": component.category,
            "name": component.name,
            "attributes": component.attributes,
        }
        for component in components
    ]
    return JsonResponse({"count": len(data), "results": data})


@require_GET
def health_check(request):
    return JsonResponse({"status": "ok"})

@login_required
@require_http_methods(["POST"])
def manage_component_import(request):
    upload = request.FILES.get("file")
    if not upload:
        return JsonResponse({"detail": "请上传 file 文件"}, status=400)
    try:
        records = parse_upload(upload)
    except (ValueError, json.JSONDecodeError) as exc:
        return JsonResponse({"detail": str(exc)}, status=400)
    preview = request.POST.get("confirm") != "true"
    if preview:
        normalized, errors = [], []
        for row, record in enumerate(records, 1):
            try: normalized.append(normalize_component_record(record))
            except ValueError as exc: errors.append({"row": row, "message": str(exc)})
        return JsonResponse({"preview": True, "records": normalized, "failed": len(errors), "errors": errors})
    return JsonResponse(import_records(records))

@login_required
@require_http_methods(["POST"])
def manage_component_create(request):
    try: data = normalize_component_record(json.loads(request.body))
    except (ValueError, json.JSONDecodeError) as exc: return JsonResponse({"detail": str(exc)}, status=400)
    obj, created = Component.objects.get_or_create(category=data["category"], name=data["name"], defaults=data)
    if not created: return JsonResponse({"detail": "组件已存在", "id": obj.id}, status=409)
    return JsonResponse({"id": obj.id, **data}, status=201)

@login_required
@require_http_methods(["PATCH", "DELETE"])
def manage_component_detail(request, pk):
    try: obj = Component.objects.get(pk=pk)
    except Component.DoesNotExist: return JsonResponse({"detail": "组件不存在"}, status=404)
    if request.method == "DELETE":
        obj.is_active = False; obj.save(update_fields=["is_active", "updated_at"])
        return JsonResponse({"id": obj.id, "is_active": False})
    try: data = normalize_component_record({**{"category": obj.category, "name": obj.name, "attributes": obj.attributes, "is_active": obj.is_active, "sort_order": obj.sort_order}, **json.loads(request.body)})
    except (ValueError, json.JSONDecodeError) as exc: return JsonResponse({"detail": str(exc)}, status=400)
    for key, value in data.items(): setattr(obj, key, value)
    obj.save(); return JsonResponse({"id": obj.id, **data})
