import json
import re
from pathlib import Path

from django.core.management.base import BaseCommand

from pc_builder.models import Component


BASE_DIR = Path(__file__).resolve().parents[3]
DATA_DIR = BASE_DIR / "frontend" / "src" / "data"


def js_array(filename, export_name):
    content = (DATA_DIR / filename).read_text(encoding="utf-8")
    match = re.search(rf"export const {export_name} = (\[.*?\])\s*$", content, re.DOTALL)
    if not match:
        raise ValueError(f"无法读取 {filename} 中的 {export_name}")
    payload = match.group(1)
    if payload.lstrip().startswith("[") and '"' in payload:
        return json.loads(payload)
    return re.findall(r"'([^']+)'", payload)


class Command(BaseCommand):
    help = "将 Vue 前端静态组件目录同步到数据库。可重复执行。"

    def handle(self, *args, **options):
        records = []
        def supported_intel_cpu(name):
            if name.startswith("Intel Core Ultra"):
                return True
            match = re.match(r"^Intel Core i[3579]-(\d+)", name)
            if not match or re.search(r"-\d+(?:X|XE)$", name):
                return False
            number = match.group(1)
            generation = int(number[0] if len(number) == 4 else number[:2])
            return generation >= 5

        cpu_models = [
            name for name in js_array("cpuModels.js", "cpuModels")
            if name.startswith("AMD Ryzen") or supported_intel_cpu(name)
        ]
        records.extend((Component.Category.CPU, name, {}) for name in cpu_models)
        records.extend((Component.Category.GPU, name, {}) for name in js_array("gpuModels.js", "gpuModels"))

        motherboard_source = (DATA_DIR / "motherboardChipsets.js").read_text(encoding="utf-8")
        for chipset, socket, ddr, platform in re.findall(
            r"\{ chipset: '([^']+)', socket: '([^']+)', ddr: \[([^]]+)\](?:, platform: '([^']+)')? \}",
            motherboard_source,
        ):
            records.append((Component.Category.MOTHERBOARD, chipset, {"socket": socket, "ddr": re.findall(r"'([^']+)'", ddr), "platform": platform}))

        for generation, capacities in {
            "DDR3": ["8GB", "16GB", "32GB"],
            "DDR4": ["8GB", "16GB", "24GB", "32GB", "48GB", "128GB"],
            "DDR5": ["8GB", "16GB", "24GB", "32GB", "48GB", "128GB"],
        }.items():
            records.extend((Component.Category.MEMORY, f"{generation} {capacity}", {"generation": generation, "capacity": capacity}) for capacity in capacities)

        for standard in ("PCIe 3.0", "PCIe 4.0", "PCIe 5.0"):
            records.extend((Component.Category.STORAGE, f"{standard} {capacity}", {"type": "pcie", "standard": standard, "capacity": capacity}) for capacity in ["256GB", "512GB", "1TB", "2TB", "4TB", "8TB"])
        records.extend((Component.Category.STORAGE, f"SATA SSD {capacity}", {"type": "sata", "standard": "SATA", "capacity": capacity}) for capacity in ["256GB", "512GB", "1TB", "2TB", "4TB", "8TB", "12TB", "16TB"])
        records.extend((Component.Category.STORAGE, f"机械硬盘 {capacity}", {"type": "hdd", "standard": "HDD", "capacity": capacity}) for capacity in ["256GB", "512GB", "1TB", "2TB", "4TB", "8TB", "12TB", "16TB", "24TB"])

        records.extend((Component.Category.POWER, f"{watts}W", {"watts": watts}) for watts in [250, 300, 350, 400, 450, 500, 550, 600, 650, 700, 750, 800, 850, 900, 1000, 1200, 1300, 1500, 1600])
        cooler_names = ["4 热管单塔风冷", "4 热管双塔风冷", "6 热管单塔风冷", "6 热管双塔风冷", "8 热管单塔风冷", "8 热管双塔风冷", "120 水冷", "240 水冷", "360 水冷", "420 水冷"]
        records.extend((Component.Category.COOLER, name, {}) for name in cooler_names)
        records.extend((Component.Category.CASE, name, {"max_size": max_size}) for name, max_size in [("ITX 机箱", 1), ("M-ATX 机箱", 2), ("ATX 机箱", 3), ("E-ATX 机箱", 4), ("开放式机箱", 4)])

        for order, (category, name, attributes) in enumerate(records):
            Component.objects.update_or_create(
                category=category,
                name=name,
                defaults={"attributes": attributes, "is_active": True, "sort_order": order},
            )

        self.stdout.write(self.style.SUCCESS(f"已同步 {len(records)} 条组件数据。"))
