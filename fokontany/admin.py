from django.contrib import admin

from .models import Fokontany, PopulationFokontany


class PopulationInline(admin.TabularInline):
    model = PopulationFokontany
    extra = 1
    fields = ("annee", "hommes", "femmes", "total", "source", "date_mise_a_jour")
    readonly_fields = ("total", "date_mise_a_jour")


@admin.register(Fokontany)
class FokontanyAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "nom",
        "responsable",
        "telephone",
        "actif",
    )
    search_fields = ("code", "nom", "responsable")
    list_filter = ("actif",)
    ordering = ("nom",)
    inlines = (PopulationInline,)


@admin.register(PopulationFokontany)
class PopulationFokontanyAdmin(admin.ModelAdmin):
    list_display = (
        "fokontany",
        "annee",
        "hommes",
        "femmes",
        "total",
        "source",
        "date_mise_a_jour",
    )
    list_filter = ("annee", "fokontany")
    search_fields = ("fokontany__nom", "source")
    readonly_fields = ("total", "date_mise_a_jour")
    ordering = ("-annee", "fokontany__nom")
