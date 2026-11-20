from django.urls import path

from . import views

app_name = "etat_civil"

urlpatterns = [
    path("", views.liste, name="liste"),
    path("ajouter/", views.ajouter, name="ajouter"),
    path("<int:pk>/modifier/", views.modifier, name="modifier"),
    path("naissances/", views.naissances_liste, name="naissances_liste"),
    path("naissances/ajouter/", views.naissance_ajouter, name="naissance_ajouter"),
    path("documents/", views.documents_liste, name="documents_liste"),
    path("documents/ajouter/", views.document_ajouter, name="document_ajouter"),
    path(
        "certificat-residence/",
        views.document_ajouter,
        {"type_document": "CERTIFICAT_RESIDENCE"},
        name="certificat_residence",
    ),
]
