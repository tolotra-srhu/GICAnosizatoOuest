from django.contrib import admin
from .models import Personnel


@admin.register(Personnel)
class PersonnelAdmin(admin.ModelAdmin):
    list_display = (
        "matricule",
        "nom",
        "prenoms",
        "fonction",
        "service",
        "fokontany",
        "telephone",
        "statut",
    )
    search_fields = (
        "matricule",
        "nom",
        "prenoms",
        "fonction",
        "service",
    )
    list_filter = ("statut", "sexe", "service", "fokontany")
    list_select_related = ("fokontany",)
    ordering = ("nom", "prenoms")