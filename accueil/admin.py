from django.contrib import admin

from .models import Actualite


@admin.register(Actualite)
class ActualiteAdmin(admin.ModelAdmin):
    list_display = ("titre", "categorie", "publiee", "date_publication", "auteur")
    list_filter = ("categorie", "publiee", "date_publication")
    search_fields = ("titre", "contenu")
    list_editable = ("publiee",)
