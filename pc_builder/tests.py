import json
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .models import Component
from .importers import normalize_component_record, import_records


class ComponentApiTests(TestCase):
    def test_api_returns_only_active_components(self):
        Component.objects.create(category=Component.Category.CPU, name="AMD Ryzen 7 7800X3D")
        Component.objects.create(category=Component.Category.CPU, name="Retired CPU", is_active=False)

        response = self.client.get(reverse("component-list"), {"category": "cpu"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 1)
        self.assertEqual(response.json()["results"][0]["name"], "AMD Ryzen 7 7800X3D")

    def test_health_check_is_available(self):
        response = self.client.get(reverse("health-check"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

class ComponentImportTests(TestCase):
    def test_normalization_and_duplicate_update(self):
        data = normalize_component_record({"category": "显卡", "name": "  RTX   5090  ", "attributes": "{\"vram\":32}", "is_active": "yes", "sort_order": "2"})
        self.assertEqual(data["category"], "gpu"); self.assertEqual(data["name"], "RTX 5090"); self.assertEqual(data["attributes"], {"vram": 32})
        result = import_records([data]); self.assertEqual(result["created"], 1)
        self.assertEqual(import_records([data])["skipped"], 1)
        data["attributes"] = {"vram": 48}; self.assertEqual(import_records([data])["updated"], 1)

    def test_invalid_batch_is_atomic_and_inactive_hidden(self):
        result = import_records([{"category": "cpu", "name": "Valid"}, {"category": "bad", "name": "Invalid"}])
        self.assertEqual(result["failed"], 1); self.assertFalse(Component.objects.exists())
        Component.objects.create(category="cooler", name="Hidden", is_active=False)
        self.assertEqual(self.client.get(reverse("component-list")).json()["count"], 0)

    def test_management_import_requires_login_and_commits_when_confirmed(self):
        url = reverse("manage-component-import")
        payload = json.dumps([{"category": "cooler", "name": "New Cooler", "attributes": {"cooling_type": "air"}}])
        denied = self.client.post(url, {"file": SimpleUploadedFile("x.json", payload.encode(), content_type="application/json")})
        self.assertIn(denied.status_code, (302, 403))
        user = get_user_model().objects.create_user("admin", password="password")
        self.client.force_login(user)
        uploaded = SimpleUploadedFile("x.json", payload.encode(), content_type="application/json")
        response = self.client.post(url, {"file": uploaded, "confirm": "true"})
        self.assertEqual(response.status_code, 200); self.assertEqual(response.json()["created"], 1)
