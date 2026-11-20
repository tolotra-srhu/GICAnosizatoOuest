from django.urls import path
from . import views

app_name = "fokontany"

urlpatterns = [
    path("", views.liste_fokontany, name="liste"),
    path("ajouter/", views.ajouter_fokontany, name="ajouter"),
    path("carte/", views.carte_fokontany, name="carte"),
    path("population/", views.population, name="population"),
    path("<int:pk>/modifier/", views.modifier_fokontany, name="modifier"),
    path("<int:pk>/", views.detail_fokontany, name="detail"),
]