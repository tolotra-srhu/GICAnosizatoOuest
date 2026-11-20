from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from comptes.forms import ConnexionForm

urlpatterns = [
    path('admin/', admin.site.urls),

    # Authentification
    path(
        'connexion/',
        auth_views.LoginView.as_view(
            template_name='registration/login.html',
            authentication_form=ConnexionForm,
        ),
        name='login',
    ),
    path('deconnexion/', auth_views.LogoutView.as_view(), name='logout'),

    # Tableau de bord et page publique
    path('', include('accueil.urls')),

    # Modules de gestion communale
    path('citoyens/', include('citoyens.urls')),
    path('etat-civil/', include('etat_civil.urls')),
    path('fokontany/', include('fokontany.urls')),
    path('personnel/', include('personnel.urls')),
    path('demandes/', include('demandes.urls')),
    path('finances/', include('finances.urls')),
    path("comptes/", include("comptes.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
