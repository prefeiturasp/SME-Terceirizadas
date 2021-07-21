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
        tem_guia_arquivada_na_lista = requisicao.guias.filter(numero_guia__in=guias, situacao=Guia.ARQUIVADA).exists()
        guias_encontradas = list(requisicao.guias.filter(numero_guia__in=guias).values_list('numero_guia', flat=True))

        if requisicao.situacao == SolicitacaoRemessa.ARQUIVADA:
            raise ValidationError('Não é possivel realizar o processo de arquivamento de uma requisição arquivada.')
        if tem_guia_arquivada_na_lista:
            raise ValidationError('Devem ser enviadas para arquivamento apenas guias ativas.')
        if set(guias_encontradas) != set(guias):
            raise ValidationError('Não é possivel arquivar guias que não pertencem a requisição enviada.')
    except ObjectDoesNotExist:
        raise ValidationError(f'Requisição {numero_requisicao} não existe.')

    requisicao.guias.filter(numero_guia__in=guias).update(situacao=Guia.ARQUIVADA)

    guias_existentes = list(requisicao.guias.values_list('numero_guia', flat=True))
    existe_guia_ativa = requisicao.guias.filter(situacao=Guia.ATIVA).exists()

    if set(guias_existentes) == set(guias) or not existe_guia_ativa:
        requisicao.arquivar_requisicao(uuid=requisicao.uuid)

def desarquiva_guias(numero_requisicao, guias):  # noqa C901
    # Método para desarquivamento da(s) guia(s) e requisições. Importante saber:
    # Se ao menos uma guia da requisição for desarquivada, a requisição também será desarquivada.

    try:
        requisicao = SolicitacaoRemessa.objects.get(numero_solicitacao=numero_requisicao)
        tem_guia_ativa_na_lista = requisicao.guias.filter(numero_guia__in=guias, situacao=Guia.ATIVA).exists()
        guias_encontradas = list(requisicao.guias.filter(numero_guia__in=guias).values_list('numero_guia', flat=True))

        if tem_guia_ativa_na_lista:
            raise ValidationError('Devem ser enviadas para desarquivamento apenas guias arquivadas.')
        if set(guias_encontradas) != set(guias):
            raise ValidationError('Não é possivel desarquivar guias que não pertencem a requisição enviada.')
    except ObjectDoesNotExist:
        raise ValidationError(f'Requisição {numero_requisicao} não existe.')

    requisicao.guias.filter(numero_guia__in=guias).update(situacao=Guia.ATIVA)

    existe_guia_ativa = requisicao.guias.filter(situacao=Guia.ATIVA).exists()
    if existe_guia_ativa:
        requisicao.desarquivar_requisicao(uuid=requisicao.uuid)
