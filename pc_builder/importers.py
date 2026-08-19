import csv
import io
import json
import unicodedata

from .models import Component

CATEGORY_ALIASES = {
    "cpu": "cpu", "CPU": "cpu", "处理器": "cpu",
    "gpu": "gpu", "显卡": "gpu", "graphics card": "gpu", "graphics_card": "gpu",
    "motherboard": "motherboard", "主板": "motherboard", "mb": "motherboard",
    "memory": "memory", "内存": "memory", "ram": "memory",
    "storage": "storage", "存储": "storage", "硬盘": "storage",
    "power": "power", "电源": "power", "psu": "power",
    "cooler": "cooler", "散热器": "cooler", "散热": "cooler",
    "case": "case", "机箱": "case",
}

def _bool(value):
    if isinstance(value, bool): return value
    if value is None or value == "": return True
    value = str(value).strip().lower()
    if value in {"true", "1", "yes", "y", "启用"}: return True
    if value in {"false", "0", "no", "n", "停用"}: return False
    raise ValueError("is_active 必须是 true/false、1/0、yes/no 或 启用/停用")

def normalize_component_record(record):
    if not isinstance(record, dict): raise ValueError("记录必须是对象")
    raw_category = str(record.get("category", "")).strip()
    category = CATEGORY_ALIASES.get(raw_category) or CATEGORY_ALIASES.get(raw_category.lower())
    if category not in {choice.value for choice in Component.Category}: raise ValueError("category 不合法")
    name = unicodedata.normalize("NFKC", str(record.get("name", ""))).strip()
    name = " ".join(name.split())
    name = name.replace("EATX", "E-ATX").replace("E ATX", "E-ATX").replace("MATX", "M-ATX").replace("M ATX", "M-ATX")
    if not name: raise ValueError("name 不能为空")
    attrs = record.get("attributes", {})
    if attrs in (None, ""): attrs = {}
    if isinstance(attrs, str):
        try: attrs = json.loads(attrs)
        except json.JSONDecodeError as exc: raise ValueError("attributes 不是合法 JSON") from exc
    if not isinstance(attrs, dict): raise ValueError("attributes 必须是 JSON 对象")
    try: sort_order = int(record.get("sort_order", 0))
    except (TypeError, ValueError) as exc: raise ValueError("sort_order 必须是非负整数") from exc
    if sort_order < 0: raise ValueError("sort_order 必须是非负整数")
    return {"category": category, "name": name, "attributes": attrs, "is_active": _bool(record.get("is_active", True)), "sort_order": sort_order}

def parse_upload(upload):
    name = upload.name.lower()
    raw = upload.read()
    if len(raw) > 5 * 1024 * 1024: raise ValueError("文件大小不能超过 5 MB")
    try: text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc: raise ValueError("文件必须使用 UTF-8 编码") from exc
    if name.endswith(".json"):
        payload = json.loads(text)
        if isinstance(payload, dict): payload = payload.get("results", [payload])
        if not isinstance(payload, list): raise ValueError("JSON 顶层必须是数组")
        return payload
    if name.endswith(".csv"):
        return list(csv.DictReader(io.StringIO(text)))
    raise ValueError("只支持 JSON 或 CSV 文件")

def import_records(records):
    normalized, errors = [], []
    for row, record in enumerate(records, 1):
        try: normalized.append(normalize_component_record(record))
        except ValueError as exc: errors.append({"row": row, "message": str(exc)})
    if errors: return {"created": 0, "updated": 0, "skipped": 0, "failed": len(errors), "errors": errors}
    created = updated = skipped = 0
    from django.db import transaction
    with transaction.atomic():
        for data in normalized:
            obj = Component.objects.filter(category=data["category"], name=data["name"]).first()
            if obj is None:
                Component.objects.create(**data); created += 1
            elif all(getattr(obj, key) == value for key, value in data.items()):
                skipped += 1
            else:
                for key, value in data.items(): setattr(obj, key, value)
                obj.save(); updated += 1
    return {"created": created, "updated": updated, "skipped": skipped, "failed": 0, "errors": []}
