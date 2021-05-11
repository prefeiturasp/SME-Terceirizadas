from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from xworkflows.base import InvalidTransitionError

from sme_terceirizadas.logistica.models import Guia


def inativa_tipos_de_embabalagem(queryset):
    for tipo_embalagem in queryset.all():
        tipo_embalagem.ativo = False
        tipo_embalagem.save()


def confirma_guias(solicitacao, user):
    guias = Guia.objects.filter(solicitacao=solicitacao)
    try:
        for guia in guias:

            guia.distribuidor_confirma_guia(user=user)
    except InvalidTransitionError as e:
        return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)
