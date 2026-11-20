from django.contrib import admin
from .models import Citoyen


@admin.register(Citoyen)
class CitoyenAdmin(admin.ModelAdmin):
    list_display = (
        "numero_citoyen",
        "nom",
        "prenoms",
        "sexe",
        "fokontany",
        "telephone",
        "actif",
    )
    search_fields = (
        "numero_citoyen",
        "nom",
        "prenoms",
        "telephone",
    )
    list_filter = ("sexe", "fokontany", "actif")
    list_select_related = ("fokontany",)
    ordering = ("nom", "prenoms")