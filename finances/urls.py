from django.urls import path

from . import views

app_name = "finances"

urlpatterns = [
    path("adidy/", views.adidy_liste, name="adidy_liste"),
    path("adidy/ajouter/", views.adidy_ajouter, name="adidy_ajouter"),
    path("association/", views.fonds_liste, name="fonds_liste"),
    path("association/ajouter/", views.fonds_ajouter, name="fonds_ajouter"),
]
