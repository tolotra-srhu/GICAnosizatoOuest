from django.urls import path
from . import views

app_name = "comptes"

urlpatterns = [
    path("chefs/", views.gestion_chefs, name="gestion_chefs"),
    path("parametres/", views.parametres, name="parametres"),
]
