import datetime

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from xworkflows import InvalidTransitionError


def date_to_string(date: datetime.date) -> str:
    assert isinstance(date, datetime.date), 'date precisa ser `datetime.date`'
    return date.strftime('%d/%m/%Y')


def string_to_date(date_string: str) -> datetime.date:
    assert isinstance(date_string, str), 'date_string precisa ser `string`'
    return datetime.datetime.strptime(date_string, '%d/%m/%Y').date()


class KitLanchePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


def cancela_solicitacao_kit_lanche_unificada(solicitacao_unificada, usuario, justificativa):
    if not solicitacao_unificada.escolas_quantidades.filter(cancelado=False):
        try:
            solicitacao_unificada.cancelar_pedido(user=usuario, justificativa=justificativa)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)
