from django.http import JsonResponse
from django.views.decorators.http import require_GET

from .models import Component


@require_GET
def component_list(request):
    category = request.GET.get("category")
    components = Component.objects.filter(is_active=True)
    if category:
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
