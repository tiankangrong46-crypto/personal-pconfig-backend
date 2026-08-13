from django.test import TestCase
from django.urls import reverse

from .models import Component


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
