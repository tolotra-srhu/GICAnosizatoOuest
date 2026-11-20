from django.contrib import admin

from .models import FondsAssociation, PaiementAdidy


@admin.register(PaiementAdidy)
class PaiementAdidyAdmin(admin.ModelAdmin):
    list_display = (
        "reference",
        "contribuable",
        "numero_carnet",
        "fokontany",
        "periode",
        "montant",
        "date_paiement",
    )
    list_filter = ("fokontany", "annee", "mois", "mode_paiement")
    search_fields = ("reference", "contribuable", "citoyen__nom")
    list_select_related = ("fokontany", "citoyen", "recu_par")
    readonly_fields = ("reference", "date_creation")


@admin.register(FondsAssociation)
class FondsAssociationAdmin(admin.ModelAdmin):
    list_display = (
        "libelle",
        "type_mouvement",
        "montant",
        "fokontany",
        "date_mouvement",
    )
    list_filter = ("type_mouvement", "fokontany")
    search_fields = ("libelle", "observations")
    list_select_related = ("fokontany", "enregistre_par")
