from django.contrib import admin

from .models import SGO, ActifNet, Flux, Fonds, ValeurLiquidative


class FondsEnLigne(admin.TabularInline):
    model = Fonds
    fields = ("nom", "categorie", "devise", "actif")
    extra = 0
    show_change_link = True


@admin.register(SGO)
class SGOAdmin(admin.ModelAdmin):
    list_display = ("nom", "pays", "couleur_primaire", "couleur_secondaire")
    prepopulated_fields = {"slug": ("nom",)}
    filter_horizontal = ("membres",)
    inlines = [FondsEnLigne]


@admin.register(Fonds)
class FondsAdmin(admin.ModelAdmin):
    list_display = ("nom", "sgo", "categorie", "devise", "actif")
    list_filter = ("sgo", "categorie", "actif")
    search_fields = ("nom", "alias")
    prepopulated_fields = {"slug": ("nom",)}


@admin.register(ValeurLiquidative)
class ValeurLiquidativeAdmin(admin.ModelAdmin):
    list_display = ("fonds", "date", "valeur")
    list_filter = ("fonds__sgo", "fonds")
    date_hierarchy = "date"


@admin.register(ActifNet)
class ActifNetAdmin(admin.ModelAdmin):
    list_display = ("fonds", "date", "montant")
    list_filter = ("fonds__sgo", "fonds")
    date_hierarchy = "date"


@admin.register(Flux)
class FluxAdmin(admin.ModelAdmin):
    list_display = ("fonds", "date", "sens", "type_client", "montant")
    list_filter = ("fonds__sgo", "sens", "type_client")
    date_hierarchy = "date"
