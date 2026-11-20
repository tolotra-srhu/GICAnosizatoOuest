from django.contrib import admin

from .models import ParametrePlateforme, ProfilUtilisateur


@admin.register(ProfilUtilisateur)
class ProfilUtilisateurAdmin(admin.ModelAdmin):
    list_display = ("utilisateur", "role", "fokontany")
    list_filter = ("role", "fokontany")
    search_fields = ("utilisateur__username",)


@admin.register(ParametrePlateforme)
class ParametrePlateformeAdmin(admin.ModelAdmin):
    list_display = ("cle", "libelle", "valeur")
    search_fields = ("cle", "libelle")
