from django.urls import path

from . import views

urlpatterns = [
    path("components/", views.component_list, name="component-list"),
    path("health/", views.health_check, name="health-check"),
]
