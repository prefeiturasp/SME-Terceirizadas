from django.contrib import admin

from .models import Terceirizada, Edital, Nutricionista

admin.site.register(Edital)


class NutricionistasInline(admin.TabularInline):
    model = Nutricionista
    extra = 1


@admin.register(Terceirizada)
class GrupoSuspensaoAlimentacaoModelAdmin(admin.ModelAdmin):
    inlines = [NutricionistasInline]
