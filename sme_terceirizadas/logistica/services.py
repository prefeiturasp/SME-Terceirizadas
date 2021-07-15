from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from xworkflows.base import InvalidTransitionError

from sme_terceirizadas.logistica.models import Guia, SolicitacaoRemessa


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


def arquiva_guias(numero_requisicao, guias):  # noqa C901
    # Método para arquivamento da(s) guia(s) e requisições. Importante saber:
    # Se todas as guias para arquivamento forem todas as guias da requisição,
    # além das guias, a requisição também será arquivada.

    try:
        requisicao = SolicitacaoRemessa.objects.get(numero_solicitacao=numero_requisicao)
        if requisicao.situacao == SolicitacaoRemessa.ARQUIVADA:
            raise ValidationError('Não é possivel realizar o processo de arquivamento de uma requisição arquivada.')
        if requisicao.guias.filter(numero_guia__in=guias, situacao=Guia.ARQUIVADA).exists():
            raise ValidationError('Devem ser enviadas para arquivamento apenas guias ativas.')
    except ObjectDoesNotExist:
        raise ValidationError(f'Requisição {numero_requisicao} não existe.')

    requisicao.guias.filter(numero_guia__in=guias).update(situacao=Guia.ARQUIVADA)

    guias_existentes = list(requisicao.guias.values_list('numero_guia', flat=True))
    existe_guia_ativa = requisicao.guias.filter(situacao=Guia.ATIVA).exists()

    if set(guias_existentes) == set(guias) or not existe_guia_ativa:
        requisicao.arquivar_requisicao(uuid=requisicao.uuid)
