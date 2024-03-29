import datetime

from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination


def date_to_string(date: datetime.date) -> str:
    assert isinstance(date, datetime.date), "date precisa ser `datetime.date`"  # nosec
    return date.strftime("%d/%m/%Y")


def string_to_date(date_string: str) -> datetime.date:
    assert isinstance(date_string, str), "date_string precisa ser `string`"  # nosec
    return datetime.datetime.strptime(date_string, "%d/%m/%Y").date()


class KitLanchePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


def cancela_solicitacao_kit_lanche_unificada(
    solicitacao_unificada, usuario, justificativa
):
    if not solicitacao_unificada.escolas_quantidades.filter(cancelado=False):
        solicitacao_unificada.cancelar_pedido(user=usuario, justificativa=justificativa)


def valida_dia_cancelamento(dia_antecedencia, data_do_evento, dias_para_cancelar):
    if data_do_evento <= dia_antecedencia:
        raise ValidationError(
            f"Só pode cancelar com no mínimo {dias_para_cancelar} dia(s) de antecedência"
        )
