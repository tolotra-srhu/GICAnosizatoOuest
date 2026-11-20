from django.urls import path
from . import views

app_name = 'accueil'

urlpatterns = [
    path('', views.accueil, name='accueil'),
    path('commune/', views.commune, name='commune'),
    path('tableau-de-bord/', views.dashboard, name='dashboard'),
]
