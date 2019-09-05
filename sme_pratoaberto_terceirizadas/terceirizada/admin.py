from django.contrib import admin

from .models import Contrato, Edital, Nutricionista, Terceirizada, VigenciaContrato


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


class ContratoInline(admin.TabularInline):
    model = Contrato
    extra = 1


@admin.register(Edital)
class EditalModelAdmin(admin.ModelAdmin):
    inlines = [ContratoInline]
