from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from xworkflows.base import InvalidTransitionError

from sme_terceirizadas.dados_comuns.fluxo_status import GuiaRemessaWorkFlow as GuiaStatus
from sme_terceirizadas.eol_servico.utils import EOLPapaService
from sme_terceirizadas.logistica.models import Guia, SolicitacaoRemessa

from ..dados_comuns.models import LogSolicitacoesUsuario


def inativa_tipos_de_embabalagem(queryset):
    for tipo_embalagem in queryset.all():
        tipo_embalagem.ativo = False
        tipo_embalagem.save()


def confirma_guias(solicitacao, user):
    guias = Guia.objects.filter(solicitacao=solicitacao, status=GuiaStatus.AGUARDANDO_CONFIRMACAO)
    try:
        for guia in guias:

            guia.distribuidor_confirma_guia(user=user)
    except InvalidTransitionError as e:
        return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)


def exclui_ultima_reposicao(guia):
    reposicao = guia.conferencias.filter(eh_reposicao=True).last()
    if reposicao:
        reposicao.conferencia_dos_alimentos.all().delete()
        reposicao.delete()


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


@transaction.atomic # noqa C901
def confirma_cancelamento(numero_requisicao, guias, user):
    # Método para confirmação de cancelamento da(s) guia(s) e requisições. Importante saber:
    # Se todas as guias para cancelamento forem todas as guias da requisição,
    # além das guias, a requisição também será cancelada.

    try:
        requisicao = SolicitacaoRemessa.objects.get(numero_solicitacao=numero_requisicao)
        solicitacoes_de_cancelamento = requisicao.solicitacoes_de_cancelamento.filter(foi_confirmada=False)
        requisicao.guias.filter(numero_guia__in=guias).update(status=GuiaStatus.CANCELADA)
        existe_guia_nao_cancelada = requisicao.guias.exclude(status=GuiaStatus.CANCELADA).exists()
        guias_existentes = list(requisicao.guias.values_list('numero_guia', flat=True))

        if set(guias_existentes) == set(guias) or not existe_guia_nao_cancelada:
            requisicao.distribuidor_confirma_cancelamento(user=user)
        else:
            requisicao.salvar_log_transicao(
                status_evento=LogSolicitacoesUsuario.PAPA_CANCELA_SOLICITACAO,
                usuario=user,
                justificativa=f'Guias canceladas: {guias}'
            )
        # Envia confirmação para o papa
        if not settings.DEBUG:
            for solicitacao in solicitacoes_de_cancelamento:
                EOLPapaService.confirmacao_de_cancelamento(
                    cnpj=solicitacao.requisicao.cnpj,
                    numero_solicitacao=solicitacao.requisicao.numero_solicitacao,
                    sequencia_envio=solicitacao.sequencia_envio
                )
        # Atualiza registros das solicitações de cancelamento
        solicitacoes_de_cancelamento.update(foi_confirmada=True)
    except ObjectDoesNotExist:
        raise ValidationError(f'Requisição {numero_requisicao} não existe.')

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
