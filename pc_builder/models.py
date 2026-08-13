from django.db import models


class Component(models.Model):
    class Category(models.TextChoices):
        CPU = "cpu", "CPU"
        MOTHERBOARD = "motherboard", "主板"
        GPU = "gpu", "显卡"
        MEMORY = "memory", "内存"
        STORAGE = "storage", "存储"
        POWER = "power", "电源"
        COOLER = "cooler", "散热器"
        CASE = "case", "机箱"

    category = models.CharField("分类", max_length=20, choices=Category.choices, db_index=True)
    name = models.CharField("型号/名称", max_length=160)
    attributes = models.JSONField("兼容属性", default=dict, blank=True)
    is_active = models.BooleanField("启用", default=True)
    sort_order = models.PositiveIntegerField("排序", default=0)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "硬件型号"
        verbose_name_plural = "硬件型号"
        ordering = ["category", "sort_order", "name"]
        constraints = [
            models.UniqueConstraint(fields=["category", "name"], name="unique_component_category_name"),
        ]

    def __str__(self):
        return f"{self.get_category_display()} - {self.name}"
