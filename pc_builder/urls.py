from django.urls import path

from . import views

urlpatterns = [
    path("components/", views.component_list, name="component-list"),
    path("health/", views.health_check, name="health-check"),
    path("manage/components/import/", views.manage_component_import, name="manage-component-import"),
    path("manage/components/", views.manage_component_create, name="manage-component-create"),
    path("manage/components/<int:pk>/", views.manage_component_detail, name="manage-component-detail"),
]
