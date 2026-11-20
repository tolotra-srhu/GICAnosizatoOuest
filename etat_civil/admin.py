from django.contrib import admin

from .models import ActeEtatCivil, ActeNaissance, DocumentAdministratif


@admin.register(ActeEtatCivil)
class ActeEtatCivilAdmin(admin.ModelAdmin):
    list_display = (
        "numero_acte",
        "type_acte",
        "fokontany",
        "date_acte",
        "lieu_acte",
    )
    search_fields = ("numero_acte", "lieu_acte")
    list_filter = ("type_acte", "fokontany", "date_acte")
    list_select_related = ("fokontany",)
    ordering = ("-date_acte",)


@admin.register(ActeNaissance)
class ActeNaissanceAdmin(admin.ModelAdmin):
    list_display = (
        "numero_acte",
        "nom_enfant",
        "prenoms_enfant",
        "sexe",
        "date_naissance",
        "fokontany",
        "date_declaration",
    )
    search_fields = (
        "numero_acte",
        "nom_enfant",
        "prenoms_enfant",
        "nom_pere",
        "nom_mere",
    )
    list_filter = ("sexe", "fokontany", "date_naissance", "date_declaration")
    list_select_related = ("fokontany", "enregistre_par")
    ordering = ("-date_naissance",)
    readonly_fields = ("date_enregistrement",)


@admin.register(DocumentAdministratif)
class DocumentAdministratifAdmin(admin.ModelAdmin):
    list_display = (
        "numero",
        "type_document",
        "nom_beneficiaire",
        "fokontany",
        "date_delivrance",
    )
    list_filter = ("type_document", "fokontany", "date_delivrance")
    search_fields = ("numero", "nom_beneficiaire", "citoyen__nom")
    list_select_related = ("fokontany", "citoyen", "delivre_par")
    readonly_fields = ("date_creation",)
