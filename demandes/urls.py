from django.urls import path

from . import views

app_name = "demandes"

urlpatterns = [
    path("", views.liste, name="liste"),
    path("nouvelle/", views.creer, name="creer"),
    path("<int:pk>/", views.detail, name="detail"),
    path("<int:pk>/traiter/", views.traiter, name="traiter"),
    path("<int:pk>/annuler/", views.annuler, name="annuler"),
    path("<int:pk>/pdf/", views.pdf, name="pdf"),
    path("<int:pk>/cachet/", views.appliquer_cachet, name="appliquer_cachet"),
]
