from django.contrib import admin

from sme_terceirizadas.recebimento.forms import QuestaoForm
from sme_terceirizadas.recebimento.models import QuestaoConferencia, QuestoesPorProduto


@admin.register(QuestaoConferencia)
class QuestaoConferenciaAdmin(admin.ModelAdmin):
    form = QuestaoForm
    list_display = (
        "questao",
        "tipo_questao",
        "pergunta_obrigatoria",
        "posicao",
        "status",
    )
    ordering = (
        "posicao",
        "criado_em",
    )
    search_fields = ("questao",)
    list_filter = (
        "tipo_questao",
        "status",
    )
    list_editable = ("pergunta_obrigatoria", "posicao")
    readonly_fields = ("uuid",)


@admin.register(QuestoesPorProduto)
class QuestoesPorProdutoAdmin(admin.ModelAdmin):
    list_display = ("ficha_tecnica",)
    filter_horizontal = ("questoes_primarias", "questoes_secundarias")
