from django.contrib import admin
from rangefilter.filters import DateRangeFilter

from src.dados_comuns.constants import StringsSearchHelpText

from .models import EscolaAberta, EscolaAbertaUnidadeParticipante


@admin.register(EscolaAberta)
class EscolaAbertaAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
        "data_inicial",
        "data_final",
        "criado_por",
        "alterado_em",
    )
    list_filter = (
        ("data_inicial", DateRangeFilter),
        ("data_final", DateRangeFilter),
    )
    search_fields = ("criado_por__nome",)
    search_help_text = StringsSearchHelpText.PESQUISE_POR_NOME_DO_USUARIO.value


@admin.register(EscolaAbertaUnidadeParticipante)
class EscolaAbertaUnidadeParticipanteAdmin(admin.ModelAdmin):
    list_display = (
        "escola_aberta",
        "lote",
        "unidade_educacional",
        "num_participantes",
    )
    list_filter = ("escola_aberta", "lote", "tipos_alimentacao")
    search_fields = (
        "unidade_educacional__nome",
        "unidade_educacional__codigo_eol",
        "lote__nome",
    )
    search_help_text = (
        StringsSearchHelpText.PESQUISE_POR_NOME_DA_ESCOLA_CODIGO_EOL_DA_ESCOLA_OU_NOME_DO_LOTE.value
    )
