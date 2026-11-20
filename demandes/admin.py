from django.contrib import admin

from .models import Demande


@admin.register(Demande)
class DemandeAdmin(admin.ModelAdmin):
    list_display = (
        "objet",
        "type_demande",
        "fokontany",
        "demandeur",
        "priorite",
        "statut",
        "date_creation",
    )
    list_filter = ("type_demande", "statut", "priorite", "fokontany")
    search_fields = ("objet", "description", "fokontany__nom", "demandeur__username")
    list_select_related = ("fokontany", "demandeur", "citoyen")
    readonly_fields = ("date_creation", "date_traitement", "traite_par")
    ordering = ("-date_creation",)
