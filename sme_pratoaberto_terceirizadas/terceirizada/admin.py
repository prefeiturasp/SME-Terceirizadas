from django.contrib import admin

from .models import Terceirizada, Edital, Nutricionista, Contrato, VigenciaContrato

admin.site.register(Edital)


class NutricionistasInline(admin.TabularInline):
    model = Nutricionista
    extra = 1


@admin.register(Terceirizada)
class GrupoSuspensaoAlimentacaoModelAdmin(admin.ModelAdmin):
    inlines = [NutricionistasInline]


class VigenciaContratoInline(admin.TabularInline):
    model = VigenciaContrato
    extra = 1


@admin.register(Contrato)
class ContratoModelAdmin(admin.ModelAdmin):
    inlines = [VigenciaContratoInline]
