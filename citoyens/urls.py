from django.urls import path

from . import views

app_name = "citoyens"

urlpatterns = [
    path("", views.liste, name="liste"),
    path("ajouter/", views.ajouter, name="ajouter"),
    path("<int:pk>/modifier/", views.modifier, name="modifier"),
]
