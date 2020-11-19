from django.core.validators import MinLengthValidator
from django.db import models

from sme_terceirizadas.dados_comuns.behaviors import Logs, TemIdentificadorExternoAmigavel
from sme_terceirizadas.dados_comuns.fluxo_status import FluxoSolicitacaoRemessa
from sme_terceirizadas.dados_comuns.models import LogSolicitacoesUsuario
from sme_terceirizadas.terceirizada.models import Terceirizada

from ...dados_comuns.behaviors import ModeloBase


class SolicitacaoRemessaManager(models.Manager):

    def create_solicitacao(self, StrCnpj, StrNumSol, distribuidor=None):
        return self.create(
            cnpj=StrCnpj,
            numero_solicitacao=StrNumSol,
            distribuidor=distribuidor
        )


class SolicitacaoRemessa(ModeloBase, TemIdentificadorExternoAmigavel, Logs, FluxoSolicitacaoRemessa):
    distribuidor = models.ForeignKey(
        Terceirizada, on_delete=models.CASCADE, blank=True, null=True, related_name='solicitacoes')
    cnpj = models.CharField('CNPJ', validators=[MinLengthValidator(14)], max_length=14)
    numero_solicitacao = models.CharField('Número da solicitação', blank=True, max_length=100)

    objects = SolicitacaoRemessaManager()

    def salvar_log_transicao(self, status_evento, usuario, **kwargs):
        justificativa = kwargs.get('justificativa', '')
        resposta_sim_nao = kwargs.get('resposta_sim_nao', False)
        LogSolicitacoesUsuario.objects.create(
            descricao=str(self),
            status_evento=status_evento,
            solicitacao_tipo=LogSolicitacoesUsuario.SOLICITACAO_REMESSA_PAPA,
            usuario=usuario,
            uuid_original=self.uuid,
            justificativa=justificativa,
            resposta_sim_nao=resposta_sim_nao
        )

    def __str__(self):
        return f'Solicitação: {self.numero_solicitacao} - Status: {self.status}'

    class Meta:
        verbose_name = 'Solicitação Remessa'
        verbose_name_plural = 'Solicitações Remessas'
