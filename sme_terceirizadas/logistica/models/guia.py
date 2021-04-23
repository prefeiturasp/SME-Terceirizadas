from django.db import models

from ...dados_comuns.behaviors import ModeloBase
from ...dados_comuns.fluxo_status import FluxoGuiaRemessa
from ...dados_comuns.models import LogSolicitacoesUsuario
from ...escola.models import Escola
from .solicitacao import SolicitacaoRemessa


class GuiaManager(models.Manager):

    def create_guia(self, StrNumGui, DtEntrega, StrCodUni, StrNomUni,
                    StrEndUni, StrNumUni, StrBaiUni, StrCepUni,
                    StrCidUni, StrEstUni, StrConUni, StrTelUni,
                    solicitacao, escola):
        return self.create(
            numero_guia=StrNumGui,
            data_entrega=DtEntrega,
            codigo_unidade=StrCodUni,
            nome_unidade=StrNomUni,
            endereco_unidade=StrEndUni,
            numero_unidade=StrNumUni,
            bairro_unidade=StrBaiUni,
            cep_unidade=StrCepUni,
            cidade_unidade=StrCidUni,
            estado_unidade=StrEstUni,
            contato_unidade=StrConUni,
            telefone_unidade=StrTelUni,
            solicitacao=solicitacao,
            escola=escola
        )


class Guia(ModeloBase, FluxoGuiaRemessa):

    numero_guia = models.CharField('Número da guia', blank=True, max_length=100, unique=True)
    solicitacao = models.ForeignKey(
        SolicitacaoRemessa, on_delete=models.CASCADE, blank=True, null=True, related_name='guias')
    data_entrega = models.DateField('Data da entrega')
    codigo_unidade = models.CharField('Código da unidade', blank=True, max_length=10)
    nome_unidade = models.CharField('Nome da unidade', blank=True, max_length=150)
    escola = models.ForeignKey(Escola, on_delete=models.SET_NULL, blank=True, null=True)
    endereco_unidade = models.CharField('Endereço da unidade', blank=True, max_length=300)
    numero_unidade = models.CharField('Número da unidade', blank=True, max_length=10)
    bairro_unidade = models.CharField('Bairro da unidade', blank=True, max_length=100)
    cep_unidade = models.CharField('CEP da unidade', blank=True, max_length=20)
    cidade_unidade = models.CharField('Cidade da unidade', blank=True, max_length=100)
    estado_unidade = models.CharField('Estado da unidade', blank=True, max_length=2)
    contato_unidade = models.CharField('Contato na unidade', blank=True, max_length=150)
    telefone_unidade = models.CharField('Telefone da unidade', blank=True, default='', max_length=20)

    objects = GuiaManager()

    def as_dict(self):
        return dict((f.name, getattr(self, f.name)) for f in self._meta.fields)

    def salvar_log_transicao(self, status_evento, usuario, **kwargs):
        justificativa = kwargs.get('justificativa', '')
        resposta_sim_nao = kwargs.get('resposta_sim_nao', False)
        log_transicao = LogSolicitacoesUsuario.objects.create(
            descricao=str(self),
            status_evento=status_evento,
            solicitacao_tipo=LogSolicitacoesUsuario.SOLICITACAO_REMESSA_PAPA,
            usuario=usuario,
            uuid_original=self.uuid,
            justificativa=justificativa,
            resposta_sim_nao=resposta_sim_nao
        )
        return log_transicao

    def __str__(self):
        return f'Guia: {self.numero_guia} da solicitação: {self.solicitacao.numero_solicitacao}'

    class Meta:
        verbose_name = 'Guia de Remessa'
        verbose_name_plural = 'Guias de Remessas'
