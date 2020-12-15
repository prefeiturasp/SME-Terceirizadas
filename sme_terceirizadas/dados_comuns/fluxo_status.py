"""Classes de apoio devem ser usadas em conjunto com as classes abstratas de fluxo.

Na pasta docs tem os BMPNs dos fluxos
"""
import datetime

import xworkflows
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.template.loader import render_to_string
from django_xworkflows import models as xwf_models

from ..escola import models as m
from ..perfil.models import Usuario
from .constants import (
    ADMINISTRADOR_DIETA_ESPECIAL,
    ADMINISTRADOR_GESTAO_ALIMENTACAO_TERCEIRIZADA,
    COORDENADOR_DIETA_ESPECIAL,
    COORDENADOR_GESTAO_ALIMENTACAO_TERCEIRIZADA,
    TIPO_SOLICITACAO_DIETA
)
from .models import AnexoLogSolicitacoesUsuario, LogSolicitacoesUsuario
from .tasks import envia_email_em_massa_task, envia_email_unico_task
from .utils import convert_base64_to_contentfile


class PedidoAPartirDaEscolaWorkflow(xwf_models.Workflow):
    # leia com atenção:
    # https://django-xworkflows.readthedocs.io/en/latest/index.html
    log_model = ''  # Disable logging to database

    RASCUNHO = 'RASCUNHO'  # INICIO
    DRE_A_VALIDAR = 'DRE_A_VALIDAR'
    DRE_VALIDADO = 'DRE_VALIDADO'
    # PODE HAVER LOOP AQUI...
    DRE_PEDIU_ESCOLA_REVISAR = 'DRE_PEDIU_ESCOLA_REVISAR'
    DRE_NAO_VALIDOU_PEDIDO_ESCOLA = 'DRE_NAO_VALIDOU_PEDIDO_ESCOLA'  # FIM DE FLUXO
    CODAE_AUTORIZADO = 'CODAE_AUTORIZADO'
    CODAE_QUESTIONADO = 'CODAE_QUESTIONADO'
    CODAE_NEGOU_PEDIDO = 'CODAE_NEGOU_PEDIDO'  # FIM, NOTIFICA ESCOLA E DRE
    TERCEIRIZADA_RESPONDEU_QUESTIONAMENTO = 'TERCEIRIZADA_RESPONDEU_QUESTIONAMENTO'
    # FIM, NOTIFICA ESCOLA, DRE E CODAE
    TERCEIRIZADA_TOMOU_CIENCIA = 'TERCEIRIZADA_TOMOU_CIENCIA'

    # UM STATUS POSSIVEL, QUE PODE SER ATIVADO PELA ESCOLA EM ATE X HORAS ANTES
    # AS TRANSIÇÕES NÃO ENXERGAM ESSE STATUS
    ESCOLA_CANCELOU = 'ESCOLA_CANCELOU'

    # TEM UMA ROTINA QUE CANCELA CASO O PEDIDO TENHA PASSADO DO DIA E NÃO TENHA TERMINADO O FLUXO
    # AS TRANSIÇÕES NÃO ENXERGAM ESSE STATUS
    CANCELADO_AUTOMATICAMENTE = 'CANCELADO_AUTOMATICAMENTE'

    states = (
        (RASCUNHO, 'Rascunho'),
        (DRE_A_VALIDAR, 'DRE a validar'),
        (DRE_VALIDADO, 'DRE validado'),
        (DRE_PEDIU_ESCOLA_REVISAR, 'Escola tem que revisar o pedido'),
        (DRE_NAO_VALIDOU_PEDIDO_ESCOLA, 'DRE não validou pedido da escola'),
        (CODAE_AUTORIZADO, 'CODAE autorizou pedido'),
        (CODAE_QUESTIONADO,
         'CODAE questionou terceirizada se é possível atender a solicitação'),
        (CODAE_NEGOU_PEDIDO, 'CODAE negou pedido'),
        (TERCEIRIZADA_RESPONDEU_QUESTIONAMENTO,
         'Terceirizada respondeu se é possível atender a solicitação'),
        (TERCEIRIZADA_TOMOU_CIENCIA, 'Terceirizada tomou'),
        (ESCOLA_CANCELOU, 'Escola cancelou'),
        (CANCELADO_AUTOMATICAMENTE, 'Cancelamento automático'),
    )

    transitions = (
        ('inicia_fluxo', RASCUNHO, DRE_A_VALIDAR),
        ('dre_valida', DRE_A_VALIDAR, DRE_VALIDADO),
        ('dre_pede_revisao', DRE_A_VALIDAR, DRE_PEDIU_ESCOLA_REVISAR),
        ('dre_nao_valida', DRE_A_VALIDAR, DRE_NAO_VALIDOU_PEDIDO_ESCOLA),
        ('escola_revisa', DRE_PEDIU_ESCOLA_REVISAR, DRE_A_VALIDAR),
        ('codae_autoriza', DRE_VALIDADO, CODAE_AUTORIZADO),
        ('codae_questiona', DRE_VALIDADO, CODAE_QUESTIONADO),
        ('codae_autoriza_questionamento',
         TERCEIRIZADA_RESPONDEU_QUESTIONAMENTO, CODAE_AUTORIZADO),
        ('codae_nega_questionamento',
         TERCEIRIZADA_RESPONDEU_QUESTIONAMENTO, CODAE_NEGOU_PEDIDO),
        ('codae_nega', DRE_VALIDADO, CODAE_NEGOU_PEDIDO),
        ('terceirizada_responde_questionamento',
         CODAE_QUESTIONADO, TERCEIRIZADA_RESPONDEU_QUESTIONAMENTO),
        ('terceirizada_toma_ciencia', CODAE_AUTORIZADO, TERCEIRIZADA_TOMOU_CIENCIA),
    )

    initial_state = RASCUNHO


class PedidoAPartirDaDiretoriaRegionalWorkflow(xwf_models.Workflow):
    # leia com atenção:
    # https://django-xworkflows.readthedocs.io/en/latest/index.html

    log_model = ''  # Disable logging to database

    RASCUNHO = 'RASCUNHO'  # INICIO
    CODAE_A_AUTORIZAR = 'CODAE_A_AUTORIZAR'
    # PODE HAVER LOOP AQUI...
    CODAE_PEDIU_DRE_REVISAR = 'DRE_PEDE_ESCOLA_REVISAR'
    CODAE_NEGOU_PEDIDO = 'CODAE_NEGOU_PEDIDO'  # FIM DE FLUXO
    CODAE_AUTORIZADO = 'CODAE_AUTORIZADO'
    CODAE_QUESTIONADO = 'CODAE_QUESTIONADO'
    # FIM, NOTIFICA ESCOLA, DRE E CODAE
    TERCEIRIZADA_TOMOU_CIENCIA = 'TERCEIRIZADA_TOMOU_CIENCIA'
    TERCEIRIZADA_RESPONDEU_QUESTIONAMENTO = 'TERCEIRIZADA_RESPONDEU_QUESTIONAMENTO'

    # UM STATUS POSSIVEL, QUE PODE SER ATIVADO PELA DRE EM ATE X HORAS ANTES
    # AS TRANSIÇÕES NÃO ENXERGAM ESSE STATUS
    DRE_CANCELOU = 'DRE_CANCELOU'

    # TEM UMA ROTINA QUE CANCELA CASO O PEDIDO TENHA PASSADO DO DIA E NÃO TENHA TERMINADO O FLUXO
    # AS TRANSIÇÕES NÃO ENXERGAM ESSE STATUS
    CANCELAMENTO_AUTOMATICO = 'CANCELAMENTO_AUTOMATICO'

    states = (
        (RASCUNHO, 'Rascunho'),
        (CODAE_A_AUTORIZAR, 'CODAE a autorizar'),
        (CODAE_PEDIU_DRE_REVISAR, 'DRE tem que revisar o pedido'),
        (CODAE_NEGOU_PEDIDO, 'CODAE negou o pedido da DRE'),
        (CODAE_AUTORIZADO, 'CODAE autorizou'),
        (CODAE_QUESTIONADO,
         'CODAE questionou terceirizada se é possível atender a solicitação'),
        (TERCEIRIZADA_TOMOU_CIENCIA, 'Terceirizada tomou ciencia'),
        (TERCEIRIZADA_RESPONDEU_QUESTIONAMENTO,
         'Terceirizada respondeu se é possível atender a solicitação'),
        (CANCELAMENTO_AUTOMATICO, 'Cancelamento automático'),
        (DRE_CANCELOU, 'DRE cancelou'),
    )

    transitions = (
        ('inicia_fluxo', RASCUNHO, CODAE_A_AUTORIZAR),
        ('codae_pede_revisao', CODAE_A_AUTORIZAR, CODAE_PEDIU_DRE_REVISAR),
        ('codae_nega', CODAE_A_AUTORIZAR, CODAE_NEGOU_PEDIDO),
        ('dre_revisa', CODAE_PEDIU_DRE_REVISAR, CODAE_A_AUTORIZAR),
        ('codae_autoriza', CODAE_A_AUTORIZAR, CODAE_AUTORIZADO),
        ('codae_questiona', CODAE_A_AUTORIZAR, CODAE_QUESTIONADO),
        ('codae_autoriza_questionamento',
         TERCEIRIZADA_RESPONDEU_QUESTIONAMENTO, CODAE_AUTORIZADO),
        ('codae_nega_questionamento',
         TERCEIRIZADA_RESPONDEU_QUESTIONAMENTO, CODAE_NEGOU_PEDIDO),
        ('terceirizada_toma_ciencia', CODAE_AUTORIZADO, TERCEIRIZADA_TOMOU_CIENCIA),
        ('terceirizada_responde_questionamento',
         CODAE_QUESTIONADO, TERCEIRIZADA_RESPONDEU_QUESTIONAMENTO)
    )

    initial_state = RASCUNHO


class InformativoPartindoDaEscolaWorkflow(xwf_models.Workflow):
    # leia com atenção:
    # https://django-xworkflows.readthedocs.io/en/latest/index.html
    log_model = ''  # Disable logging to database

    RASCUNHO = 'RASCUNHO'  # INICIO
    INFORMADO = 'INFORMADO'
    TERCEIRIZADA_TOMOU_CIENCIA = 'TERCEIRIZADA_TOMOU_CIENCIA'

    states = (
        (RASCUNHO, 'Rascunho'),
        (INFORMADO, 'Informado'),
        (TERCEIRIZADA_TOMOU_CIENCIA, 'Terceirizada toma ciencia'),
    )

    transitions = (
        ('informa', RASCUNHO, INFORMADO),
        ('terceirizada_toma_ciencia', INFORMADO, TERCEIRIZADA_TOMOU_CIENCIA),
    )

    initial_state = RASCUNHO


class SolicitacaoRemessaWorkFlow(xwf_models.Workflow):
    log_model = ''  # Disable logging to database

    AGUARDANDO_ENVIO = 'AGUARDANDO_ENVIO'
    DILOG_ENVIA = 'DILOG_ENVIA'
    PAPA_CANCELA = 'CANCELADA'
    DISTRIBUIDOR_CONFIRMA = 'DISTRIBUIDOR_CONFIRMA'
    DISTRIBUIDOR_SOLICITA_ALTERACAO = 'DISTRIBUIDOR_SOLICITA_ALTERACAO'

    states = (
        (AGUARDANDO_ENVIO, 'Aguardando envio'),
        (DILOG_ENVIA, 'Enviada'),
        (PAPA_CANCELA, 'Cancelada'),
        (DISTRIBUIDOR_CONFIRMA, 'Confirmada'),
        (DISTRIBUIDOR_SOLICITA_ALTERACAO, 'Em análise')
    )

    transitions = (
        ('inicia_fluxo', AGUARDANDO_ENVIO, DILOG_ENVIA),
        ('empresa_atende', DILOG_ENVIA, DISTRIBUIDOR_CONFIRMA),
        ('solicita_alteracao', DILOG_ENVIA, DISTRIBUIDOR_SOLICITA_ALTERACAO),
        ('cancela_solicitacao', [AGUARDANDO_ENVIO, DILOG_ENVIA, DISTRIBUIDOR_CONFIRMA, DISTRIBUIDOR_SOLICITA_ALTERACAO,
                                 PAPA_CANCELA], PAPA_CANCELA)
    )

    initial_state = AGUARDANDO_ENVIO


class DietaEspecialWorkflow(xwf_models.Workflow):
    # leia com atenção:
    # https://django-xworkflows.readthedocs.io/en/latest/index.html
    log_model = ''  # Disable logging to database

    RASCUNHO = 'RASCUNHO'
    CODAE_A_AUTORIZAR = 'CODAE_A_AUTORIZAR'  # INICIO
    CODAE_NEGOU_PEDIDO = 'CODAE_NEGOU_PEDIDO'
    CODAE_AUTORIZADO = 'CODAE_AUTORIZADO'
    TERCEIRIZADA_TOMOU_CIENCIA = 'TERCEIRIZADA_TOMOU_CIENCIA'
    ESCOLA_SOLICITOU_INATIVACAO = 'ESCOLA_SOLICITOU_INATIVACAO'
    CODAE_NEGOU_INATIVACAO = 'CODAE_NEGOU_INATIVACAO'
    CODAE_AUTORIZOU_INATIVACAO = 'CODAE_AUTORIZOU_INATIVACAO'
    TERCEIRIZADA_TOMOU_CIENCIA_INATIVACAO = 'TERCEIRIZADA_TOMOU_CIENCIA_INATIVACAO'
    TERMINADA_AUTOMATICAMENTE_SISTEMA = 'TERMINADA_AUTOMATICAMENTE_SISTEMA'

    ESCOLA_CANCELOU = 'ESCOLA_CANCELOU'

    states = (
        (RASCUNHO, 'Rascunho'),
        (CODAE_A_AUTORIZAR, 'CODAE a autorizar'),
        (CODAE_NEGOU_PEDIDO, 'CODAE negou a solicitação'),
        (CODAE_AUTORIZADO, 'CODAE autorizou'),
        (TERCEIRIZADA_TOMOU_CIENCIA, 'Terceirizada toma ciencia'),
        (ESCOLA_CANCELOU, 'Escola cancelou'),
        (ESCOLA_SOLICITOU_INATIVACAO, 'Escola solicitou inativação'),
        (CODAE_NEGOU_INATIVACAO, 'CODAE negou a inativação'),
        (CODAE_AUTORIZOU_INATIVACAO, 'CODAE autorizou a inativação'),
        (TERCEIRIZADA_TOMOU_CIENCIA_INATIVACAO,
         'Terceirizada tomou ciência da inativação'),
        (TERMINADA_AUTOMATICAMENTE_SISTEMA, 'Data de término atingida')
    )

    transitions = (
        ('inicia_fluxo', RASCUNHO, CODAE_A_AUTORIZAR),
        ('codae_nega', [CODAE_A_AUTORIZAR,
                        ESCOLA_SOLICITOU_INATIVACAO], CODAE_NEGOU_PEDIDO),
        ('codae_autoriza', CODAE_A_AUTORIZAR, CODAE_AUTORIZADO),
        ('terceirizada_toma_ciencia', CODAE_AUTORIZADO, TERCEIRIZADA_TOMOU_CIENCIA),
        ('cancelar_pedido', CODAE_A_AUTORIZAR, ESCOLA_CANCELOU),
        ('inicia_fluxo_inativacao', [
         CODAE_AUTORIZADO, TERCEIRIZADA_TOMOU_CIENCIA], ESCOLA_SOLICITOU_INATIVACAO),
        ('codae_nega_inativacao', ESCOLA_SOLICITOU_INATIVACAO, CODAE_NEGOU_INATIVACAO),
        ('codae_autoriza_inativacao',
         ESCOLA_SOLICITOU_INATIVACAO, CODAE_AUTORIZOU_INATIVACAO),
        ('terceirizada_toma_ciencia_inativacao',
         CODAE_AUTORIZOU_INATIVACAO, TERCEIRIZADA_TOMOU_CIENCIA_INATIVACAO),
    )

    initial_state = RASCUNHO


class HomologacaoProdutoWorkflow(xwf_models.Workflow):
    # leia com atenção:
    # https://django-xworkflows.readthedocs.io/en/latest/index.html
    log_model = ''  # Disable logging to database

    RASCUNHO = 'RASCUNHO'
    CODAE_PENDENTE_HOMOLOGACAO = 'CODAE_PENDENTE_HOMOLOGACAO'  # INICIO
    CODAE_HOMOLOGADO = 'CODAE_HOMOLOGADO'
    CODAE_NAO_HOMOLOGADO = 'CODAE_NAO_HOMOLOGADO'
    CODAE_QUESTIONADO = 'CODAE_QUESTIONADO'
    CODAE_PEDIU_ANALISE_SENSORIAL = 'CODAE_PEDIU_ANALISE_SENSORIAL'
    TERCEIRIZADA_CANCELOU = 'TERCEIRIZADA_CANCELOU'
    INATIVA = 'HOMOLOGACAO_INATIVA'
    CODAE_SUSPENDEU = 'CODAE_SUSPENDEU'
    ESCOLA_OU_NUTRICIONISTA_RECLAMOU = 'ESCOLA_OU_NUTRICIONISTA_RECLAMOU'
    CODAE_PEDIU_ANALISE_RECLAMACAO = 'CODAE_PEDIU_ANALISE_RECLAMACAO'
    TERCEIRIZADA_RESPONDEU_RECLAMACAO = 'TERCEIRIZADA_RESPONDEU_RECLAMACAO'
    CODAE_AUTORIZOU_RECLAMACAO = 'CODAE_AUTORIZOU_RECLAMACAO'

    states = (
        (RASCUNHO, 'Rascunho'),
        (CODAE_PENDENTE_HOMOLOGACAO, 'Pendente homologação da CODAE'),
        (CODAE_HOMOLOGADO, 'CODAE homologou'),
        (CODAE_NAO_HOMOLOGADO, 'CODAE não homologou'),
        (CODAE_QUESTIONADO, 'CODAE pediu correção'),
        (CODAE_PEDIU_ANALISE_SENSORIAL, 'CODAE pediu análise sensorial'),
        (TERCEIRIZADA_CANCELOU, 'Terceirizada cancelou homologação'),
        (INATIVA, 'Homologação inativada'),
        (CODAE_SUSPENDEU, 'CODAE suspendeu o produto'),
        (ESCOLA_OU_NUTRICIONISTA_RECLAMOU,
         'Escola/Nutricionista reclamou do produto'),
        (CODAE_PEDIU_ANALISE_RECLAMACAO, 'CODAE pediu análise da reclamação'),
        (TERCEIRIZADA_RESPONDEU_RECLAMACAO, 'Terceirizada respondeu a reclamação'),
        (CODAE_AUTORIZOU_RECLAMACAO, 'CODAE autorizou reclamação')
    )

    transitions = (
        ('inicia_fluxo', [RASCUNHO, CODAE_AUTORIZOU_RECLAMACAO],
         CODAE_PENDENTE_HOMOLOGACAO),
        ('codae_homologa', [CODAE_PENDENTE_HOMOLOGACAO, CODAE_PEDIU_ANALISE_SENSORIAL,
                            TERCEIRIZADA_RESPONDEU_RECLAMACAO, CODAE_SUSPENDEU,
                            ESCOLA_OU_NUTRICIONISTA_RECLAMOU],
         CODAE_HOMOLOGADO),
        ('codae_nao_homologa', [CODAE_PENDENTE_HOMOLOGACAO,
                                CODAE_PEDIU_ANALISE_SENSORIAL], CODAE_NAO_HOMOLOGADO),
        ('codae_questiona', CODAE_PENDENTE_HOMOLOGACAO, CODAE_QUESTIONADO),
        ('terceirizada_responde_questionamento',
         CODAE_QUESTIONADO, CODAE_PENDENTE_HOMOLOGACAO),
        ('codae_pede_analise_sensorial',
         CODAE_PENDENTE_HOMOLOGACAO, CODAE_PEDIU_ANALISE_SENSORIAL),
        ('terceirizada_responde_analise_sensorial',
         CODAE_PEDIU_ANALISE_SENSORIAL, CODAE_PENDENTE_HOMOLOGACAO),
        ('codae_suspende', CODAE_HOMOLOGADO, CODAE_SUSPENDEU),
        ('codae_ativa', CODAE_SUSPENDEU, CODAE_HOMOLOGADO),
        ('escola_ou_nutricionista_reclamou',
         CODAE_HOMOLOGADO, ESCOLA_OU_NUTRICIONISTA_RECLAMOU),
        ('codae_pediu_analise_reclamacao',
            [ESCOLA_OU_NUTRICIONISTA_RECLAMOU, TERCEIRIZADA_RESPONDEU_RECLAMACAO],
            CODAE_PEDIU_ANALISE_RECLAMACAO),
        ('terceirizada_responde_reclamacao',
         CODAE_PEDIU_ANALISE_RECLAMACAO, TERCEIRIZADA_RESPONDEU_RECLAMACAO),
        ('codae_autorizou_reclamacao',
            [CODAE_PEDIU_ANALISE_RECLAMACAO,
             ESCOLA_OU_NUTRICIONISTA_RECLAMOU,
             TERCEIRIZADA_RESPONDEU_RECLAMACAO],
         CODAE_AUTORIZOU_RECLAMACAO),
        ('codae_recusou_reclamacao',
            [CODAE_PEDIU_ANALISE_RECLAMACAO,
             ESCOLA_OU_NUTRICIONISTA_RECLAMOU,
             TERCEIRIZADA_RESPONDEU_RECLAMACAO],
            CODAE_HOMOLOGADO),
        ('inativa_homologacao',
         [CODAE_SUSPENDEU, ESCOLA_OU_NUTRICIONISTA_RECLAMOU, CODAE_QUESTIONADO, CODAE_HOMOLOGADO,
          CODAE_NAO_HOMOLOGADO, CODAE_AUTORIZOU_RECLAMACAO], INATIVA),
    )

    initial_state = RASCUNHO


class FluxoSolicitacaoRemessa(xwf_models.WorkflowEnabled, models.Model):
    workflow_class = SolicitacaoRemessaWorkFlow
    status = xwf_models.StateField(workflow_class)

    def salvar_log_transicao(self, status_evento, usuario, **kwargs):
        raise NotImplementedError('Deve criar um método salvar_log_transicao')

    def _preenche_template_e_envia_email(self, assunto, titulo, user, partes_interessadas):
        raise NotImplementedError('Deve criar um método de envio de email as partes interessadas')  # noqa

    def _envia_email_dilog_envia_solicitacao_para_distibuidor(self, log_transicao):
        html = render_to_string(
            template_name='logistica_dilog_envia_solicitacao.html',
            context={
                'titulo': f'Nova solicitação N° {self.numero_solicitacao} para Entrega de Alimento',
                'solicitacao': self.numero_solicitacao,
                'log_transicao': log_transicao,
            }
        )
        envia_email_unico_task.delay(
            assunto=f'[SIGPAE] Nova solicitação N° {self.numero_solicitacao} para Entrega de Alimento',
            email=self.distribuidor.responsavel_email,
            corpo='',
            html=html
        )

    @xworkflows.after_transition('inicia_fluxo')
    def _inicia_fluxo_hook(self, *args, **kwargs):
        user = kwargs['user']
        log_transicao = self.salvar_log_transicao(status_evento=LogSolicitacoesUsuario.DILOG_ENVIA_SOLICITACAO,
                                                  usuario=user,
                                                  justificativa=kwargs.get('justificativa', ''))

        self._envia_email_dilog_envia_solicitacao_para_distibuidor(log_transicao=log_transicao)

    @xworkflows.after_transition('empresa_atende')
    def _empresa_atende_hook(self, *args, **kwargs):
        user = kwargs['user']
        self.salvar_log_transicao(status_evento=LogSolicitacoesUsuario.DISTRIBUIDOR_CONFIRMA_SOLICITACAO,
                                  usuario=user,
                                  justificativa=kwargs.get('justificativa', ''))

    @xworkflows.after_transition('cancela_solicitacao')
    def _cancela_solicitacao_hook(self, *args, **kwargs):
        user = kwargs['user']
        self.salvar_log_transicao(status_evento=LogSolicitacoesUsuario.PAPA_CANCELA_SOLICITACAO,
                                  usuario=user,
                                  justificativa=kwargs.get('justificativa', ''))

    class Meta:
        abstract = True


class FluxoHomologacaoProduto(xwf_models.WorkflowEnabled, models.Model):
    workflow_class = HomologacaoProdutoWorkflow
    status = xwf_models.StateField(workflow_class)
    DIAS_PARA_CANCELAR = 2

    rastro_terceirizada = models.ForeignKey('terceirizada.Terceirizada',
                                            on_delete=models.DO_NOTHING,
                                            null=True,
                                            blank=True,
                                            related_name='%(app_label)s_%(class)s_rastro_terceirizada',
                                            editable=False)

    def _salva_rastro_solicitacao(self):
        self.rastro_terceirizada = self.criado_por.vinculo_atual.instituicao
        self.save()

    @property
    def pode_excluir(self):
        return self.status == self.workflow_class.RASCUNHO

    @property
    def template_mensagem(self):
        raise NotImplementedError(
            'Deve criar um property que recupera o assunto e corpo mensagem desse objeto')

    def salvar_log_transicao(self, status_evento, usuario, **kwargs):
        raise NotImplementedError('Deve criar um método salvar_log_transicao')

    #
    # Esses hooks são chamados automaticamente após a
    # transition do status ser chamada.
    # Ex. >>> alimentacao_continua.inicia_fluxo(param1, param2, key1='val')
    #

    def _preenche_template_e_envia_email(self, assunto, titulo, user, partes_interessadas):
        template = 'fluxo_autorizar_negar_cancelar.html'
        dados_template = {'titulo': titulo, 'tipo_solicitacao': self.DESCRICAO,
                          'movimentacao_realizada': str(self.status), 'perfil_que_autorizou': user.nome}
        html = render_to_string(template, dados_template)
        envia_email_em_massa_task.delay(
            assunto=assunto,
            corpo='',
            emails=partes_interessadas,
            template='fluxo_autorizar_negar_cancelar.html',
            dados_template={'titulo': titulo, 'tipo_solicitacao': self.DESCRICAO,
                            'movimentacao_realizada': str(self.status), 'perfil_que_autorizou': user.nome},
            html=html
        )

    def _partes_interessadas_codae_homologa(self):
        # Envia email somente para ESCOLAS selecionadas
        # e para COORDENADOR_DIETA_ESPECIAL e NUTRI_ADMIN_RESPONSAVEL.
        escolas_ids = m.Escola.objects.filter(
            enviar_email_por_produto=True
        ).values_list('id', flat=True)

        content_type = ContentType.objects.get_for_model(m.Escola)

        usuarios_escolas_selecionadas = Usuario.objects.filter(
            vinculos__object_id__in=escolas_ids,
            vinculos__content_type=content_type,
        )

        usuarios_vinculos_perfil = Usuario.objects.filter(
            vinculos__perfil__nome__in=(
                'COORDENADOR_DIETA_ESPECIAL',
                'NUTRI_ADMIN_RESPONSAVEL',
            )
        )

        queryset = usuarios_escolas_selecionadas | usuarios_vinculos_perfil
        return [usuario.email for usuario in queryset]

    def _envia_email_codae_homologa(self, log_transicao, link_pdf):
        html = render_to_string(
            template_name='produto_codae_homologa.html',
            context={
                'titulo': 'Produto Homologado com sucesso',
                'produto': self.produto,
                'log_transicao': log_transicao,
                'link_pdf': link_pdf
            }
        )
        envia_email_em_massa_task.delay(
            assunto='Produto Homologado com sucesso',
            emails=self._partes_interessadas_codae_homologa(),
            corpo='',
            html=html
        )

    def _envia_email_codae_nao_homologa(self, log_transicao, link_pdf):
        html = render_to_string(
            template_name='produto_codae_nao_homologa.html',
            context={
                'titulo': 'Produto não homologado',
                'produto': self.produto,
                'log_transicao': log_transicao,
                'link_pdf': link_pdf
            }
        )
        envia_email_em_massa_task.delay(
            assunto='Produto não homologado',
            emails=self._partes_interessadas_codae_homologa(),
            corpo='',
            html=html
        )

    def _envia_email_codae_questiona(self, log_transicao, link_pdf):
        html = render_to_string(
            template_name='produto_codae_questiona.html',
            context={
                'titulo': 'Produto Cadastrado Exige Correção',
                'produto': self.produto,
                'log_transicao': log_transicao,
                'link_pdf': link_pdf
            }
        )
        envia_email_em_massa_task.delay(
            assunto='Produto Cadastrado Exige Correção',
            emails=[self.produto.criado_por.email],
            corpo='',
            html=html
        )

    def _envia_email_escola_ou_nutricionista_reclamou(self, reclamacao):
        html = render_to_string(
            template_name='produto_escola_ou_nutricionista_reclamou.html',
            context={
                'titulo': 'Nova reclamação de produto',
                'produto': self.produto,
                'reclamacao': reclamacao
            }
        )
        partes_interessadas = Usuario.objects.filter(vinculos__perfil__nome__in=[
            'COORDENADOR_GESTAO_PRODUTO',
            'ADMINISTRADOR_GESTAO_PRODUTO'
        ])
        envia_email_em_massa_task.delay(
            assunto='Nova reclamação de produto requer análise',
            emails=[usuario.email for usuario in partes_interessadas],
            corpo='',
            html=html
        )

    def _partes_interessadas_codae_pede_analise_sensorial(self):
        return [self.criado_por.email]

    def _envia_email_codae_pede_analise_sensorial(self, log_transicao, link_pdf):
        html = render_to_string(
            template_name='produto_codae_pede_analise_sensorial.html',
            context={
                'titulo': 'Solicitação de Análise Sensorial',
                'produto': self.produto,
                'protocolo': self.protocolo_analise_sensorial,
                'log_transicao': log_transicao,
                'link_pdf': link_pdf
            }
        )
        envia_email_em_massa_task.delay(
            assunto='[SIGPAE] Solicitação de Análise Sensorial',
            emails=self._partes_interessadas_codae_pede_analise_sensorial(),
            corpo='',
            html=html
        )

    def _partes_interessadas_codae_ativa_ou_suspende(self):
        queryset = Usuario.objects.filter(
            vinculos__perfil__nome__in=(
                'ADMINISTRADOR_TERCEIRIZADA',
            )
        )
        return [usuario.email for usuario in queryset]

    def _envia_email_codae_ativa_ou_suspende(self, log_transicao, template_name, assunto):
        html = render_to_string(
            template_name=template_name,
            context={
                'produto': self.produto,
                'log_transicao': log_transicao,
            }
        )
        usuarios_selecionados = self._partes_interessadas_codae_homologa()
        emails = self._partes_interessadas_codae_ativa_ou_suspende() + usuarios_selecionados  # noqa
        envia_email_em_massa_task.delay(
            assunto=assunto,
            emails=emails,
            corpo='',
            html=html
        )

    @xworkflows.after_transition('inicia_fluxo')
    def _inicia_fluxo_hook(self, *args, **kwargs):
        self._salva_rastro_solicitacao()
        user = kwargs['user']
        self.salvar_log_transicao(status_evento=LogSolicitacoesUsuario.INICIO_FLUXO,
                                  usuario=user,
                                  justificativa=kwargs.get('justificativa', ''))

    @xworkflows.after_transition('codae_homologa')
    def _codae_homologa_hook(self, *args, **kwargs):
        user = kwargs['user']
        log_transicao = self.salvar_log_transicao(
            status_evento=LogSolicitacoesUsuario.CODAE_HOMOLOGADO,
            usuario=user
        )
        for anexo in kwargs.get('anexos', []):
            arquivo = convert_base64_to_contentfile(anexo.pop('base64'))
            AnexoLogSolicitacoesUsuario.objects.create(
                log=log_transicao,
                arquivo=arquivo,
                nome=anexo['nome']
            )
        if not kwargs.get('nao_enviar_email', False):
            self._envia_email_codae_homologa(
                log_transicao=log_transicao, link_pdf=kwargs['link_pdf'])

    @xworkflows.after_transition('terceirizada_inativa')
    def _inativa_homologacao_hook(self, *args, **kwargs):
        user = kwargs['user']
        self.salvar_log_transicao(status_evento=LogSolicitacoesUsuario.INATIVA,
                                  usuario=user)

    @xworkflows.after_transition('codae_nao_homologa')
    def _codae_nao_homologa_hook(self, *args, **kwargs):
        user = kwargs['user']
        justificativa = kwargs.get('justificativa', '')
        log_transicao = self.salvar_log_transicao(
            status_evento=LogSolicitacoesUsuario.CODAE_NAO_HOMOLOGADO,
            usuario=user,
            justificativa=justificativa
        )
        self._envia_email_codae_nao_homologa(log_transicao, kwargs['link_pdf'])

    @xworkflows.after_transition('codae_questiona')
    def _codae_questiona_hook(self, *args, **kwargs):
        user = kwargs['user']
        justificativa = kwargs.get('justificativa', '')
        log_transicao = self.salvar_log_transicao(
            status_evento=LogSolicitacoesUsuario.CODAE_QUESTIONOU,
            usuario=user,
            justificativa=justificativa
        )
        self._envia_email_codae_questiona(
            log_transicao, link_pdf=kwargs['link_pdf'])

    @xworkflows.after_transition('codae_pede_analise_sensorial')
    def _codae_pede_analise_sensorial_hook(self, *args, **kwargs):
        user = kwargs['user']
        justificativa = kwargs.get('justificativa', '')
        log_transicao = self.salvar_log_transicao(
            status_evento=LogSolicitacoesUsuario.CODAE_PEDIU_ANALISE_SENSORIAL,
            usuario=user,
            justificativa=justificativa)
        self._envia_email_codae_pede_analise_sensorial(
            log_transicao=log_transicao, link_pdf=kwargs['link_pdf'])

    @xworkflows.after_transition('terceirizada_responde_analise_sensorial')
    def _terceirizada_responde_analise_sensorial_hook(self, *args, **kwargs):
        user = kwargs['user']
        justificativa = kwargs.get('justificativa', '')
        self.salvar_log_transicao(status_evento=LogSolicitacoesUsuario.TERCEIRIZADA_RESPONDEU_ANALISE_SENSORIAL,
                                  usuario=user,
                                  justificativa=justificativa)

    @xworkflows.after_transition('codae_pediu_analise_reclamacao')
    def _codae_pediu_analise_reclamacao_hook(self, *args, **kwargs):
        user = kwargs['user']
        justificativa = kwargs.get('justificativa', '')
        log_transicao = self.salvar_log_transicao(
            status_evento=LogSolicitacoesUsuario.CODAE_PEDIU_ANALISE_RECLAMACAO,
            usuario=user,
            justificativa=justificativa,
        )
        for anexo in kwargs.get('anexos'):
            arquivo = convert_base64_to_contentfile(anexo.pop('base64'))
            AnexoLogSolicitacoesUsuario.objects.create(
                log=log_transicao,
                arquivo=arquivo,
                nome=anexo['nome']
            )

    @xworkflows.after_transition('codae_autorizou_reclamacao')
    def _codae_autorizou_reclamacao_hook(self, *args, **kwargs):
        user = kwargs['user']
        justificativa = kwargs.get('justificativa', '')
        log_transicao = self.salvar_log_transicao(
            status_evento=LogSolicitacoesUsuario.CODAE_AUTORIZOU_RECLAMACAO,
            usuario=user,
            justificativa=justificativa,
        )
        for anexo in kwargs.get('anexos'):
            arquivo = convert_base64_to_contentfile(anexo.pop('base64'))
            AnexoLogSolicitacoesUsuario.objects.create(
                log=log_transicao,
                arquivo=arquivo,
                nome=anexo['nome']
            )

    @xworkflows.after_transition('escola_ou_nutricionista_reclamou')
    def _escola_ou_nutricionista_reclamou_hook(self, *args, **kwargs):
        user = kwargs['user']
        reclamacao = kwargs['reclamacao']
        self.salvar_log_transicao(
            status_evento=LogSolicitacoesUsuario.ESCOLA_OU_NUTRICIONISTA_RECLAMOU,
            usuario=user,
            justificativa=reclamacao['reclamacao'],
        )
        self._envia_email_escola_ou_nutricionista_reclamou(reclamacao)

    def salva_log_com_justificativa_e_anexos(self, evento, request):
        log_transicao = self.salvar_log_transicao(
            status_evento=evento,
            usuario=request.user,
            justificativa=request.data['justificativa']
        )
        for anexo in request.data.pop('anexos', []):
            arquivo = convert_base64_to_contentfile(anexo.pop('base64'))
            AnexoLogSolicitacoesUsuario.objects.create(
                log=log_transicao,
                arquivo=arquivo,
                nome=anexo['nome']
            )
        return log_transicao

    @xworkflows.after_transition('codae_suspende')
    def _codae_suspende_hook(self, *args, **kwargs):
        log_suspensao = self.salva_log_com_justificativa_e_anexos(
            LogSolicitacoesUsuario.CODAE_SUSPENDEU,
            kwargs['request']
        )
        self._envia_email_codae_ativa_ou_suspende(
            log_suspensao,
            template_name='produto_codae_suspende.html',
            assunto='[SIGPAE] Suspensão de Produto'
        )

    @xworkflows.after_transition('codae_ativa')
    def _codae_ativa_hook(self, *args, **kwargs):
        log_ativacao = self.salva_log_com_justificativa_e_anexos(
            LogSolicitacoesUsuario.CODAE_HOMOLOGADO,
            kwargs['request']
        )
        self._envia_email_codae_ativa_ou_suspende(
            log_ativacao,
            template_name='produto_codae_ativa.html',
            assunto='[SIGPAE] Ativação de Produto'
        )

    @xworkflows.after_transition('terceirizada_responde_reclamacao')
    def _terceirizada_responde_reclamacao_hook(self, *args, **kwargs):
        self.salva_log_com_justificativa_e_anexos(
            LogSolicitacoesUsuario.TERCEIRIZADA_RESPONDEU_QUESTIONAMENTO,
            kwargs['request']
        )

    class Meta:
        abstract = True


class FluxoAprovacaoPartindoDaEscola(xwf_models.WorkflowEnabled, models.Model):
    workflow_class = PedidoAPartirDaEscolaWorkflow
    status = xwf_models.StateField(workflow_class)
    DIAS_PARA_CANCELAR = 2

    rastro_escola = models.ForeignKey('escola.Escola',
                                      on_delete=models.DO_NOTHING,
                                      null=True,
                                      blank=True,
                                      related_name='%(app_label)s_%(class)s_rastro_escola',
                                      editable=False)
    rastro_dre = models.ForeignKey('escola.DiretoriaRegional',
                                   on_delete=models.DO_NOTHING,
                                   null=True,
                                   related_name='%(app_label)s_%(class)s_rastro_dre',
                                   blank=True,
                                   editable=False)
    rastro_lote = models.ForeignKey('escola.Lote',
                                    on_delete=models.DO_NOTHING,
                                    null=True,
                                    blank=True,
                                    related_name='%(app_label)s_%(class)s_rastro_lote',
                                    editable=False)
    rastro_terceirizada = models.ForeignKey('terceirizada.Terceirizada',
                                            on_delete=models.DO_NOTHING,
                                            null=True,
                                            blank=True,
                                            related_name='%(app_label)s_%(class)s_rastro_terceirizada',
                                            editable=False)

    def _salva_rastro_solicitacao(self):
        self.rastro_escola = self.escola
        self.rastro_dre = self.escola.diretoria_regional
        self.rastro_lote = self.escola.lote
        self.rastro_terceirizada = self.escola.lote.terceirizada
        self.save()

    def cancelar_pedido(self, user, justificativa):
        """O objeto que herdar de FluxoAprovacaoPartindoDaEscola, deve ter um property data.

        Dado dias de antecedencia de prazo, verifica se pode e altera o estado
        """
        dia_antecedencia = datetime.date.today(
        ) + datetime.timedelta(days=self.DIAS_PARA_CANCELAR)
        data_do_evento = self.data
        if isinstance(data_do_evento, datetime.datetime):
            # TODO: verificar por que os models estao retornando datetime em
            # vez de date
            data_do_evento = data_do_evento.date()

        if (data_do_evento > dia_antecedencia) and (self.status != self.workflow_class.ESCOLA_CANCELOU):
            self.status = self.workflow_class.ESCOLA_CANCELOU
            self.salvar_log_transicao(status_evento=LogSolicitacoesUsuario.ESCOLA_CANCELOU,
                                      usuario=user,
                                      justificativa=justificativa)
            self.save()
            # envia email para partes interessadas
            assunto = '[SIGPAE] Status de solicitação - #' + self.id_externo
            titulo = 'Status de solicitação - #' + self.id_externo
            self._preenche_template_e_envia_email(
                assunto, titulo, user, self._partes_interessadas_cancelamento)

        elif self.status == self.workflow_class.ESCOLA_CANCELOU:
            raise xworkflows.InvalidTransitionError('Já está cancelada')
        else:
            raise xworkflows.InvalidTransitionError(
                f'Só pode cancelar com no mínimo {self.DIAS_PARA_CANCELAR} dia(s) de antecedência')

    def cancelamento_automatico_apos_vencimento(self):
        """Chamado automaticamente quando o pedido já passou do dia de atendimento e não chegou ao fim do fluxo."""
        self.status = self.workflow_class.CANCELADO_AUTOMATICAMENTE

    @property
    def pode_excluir(self):
        return self.status == self.workflow_class.RASCUNHO

    @property
    def ta_na_dre(self):
        return self.status == self.workflow_class.DRE_A_VALIDAR

    @property
    def ta_na_escola(self):
        return self.status in [self.workflow_class.RASCUNHO,
                               self.workflow_class.DRE_PEDIU_ESCOLA_REVISAR]

    @property
    def ta_na_codae(self):
        return self.status == self.workflow_class.DRE_VALIDADO

    @property
    def ta_na_terceirizada(self):
        return self.status == self.workflow_class.CODAE_AUTORIZADO

    @property
    def _partes_interessadas_inicio_fluxo(self):
        """Quando a escola faz a solicitação, as pessoas da DRE são as partes interessadas.

        Será retornada uma lista de emails para envio via celery.
        """
        email_query_set = self.rastro_dre.vinculos.filter(
            ativo=True
        ).values_list('usuario__email', flat=False)
        return [email for email in email_query_set]

    @property
    def _partes_interessadas_cancelamento(self):
        """Quando a escola cancela a sua solicitação, a codae ou dre devem ser avisados caso tenha chegado neles.

        Será retornada uma lista de emails para envio via celery.
        """
        email_lista = []
        if self.ta_na_codae:
            email_query_set_dre = self.rastro_dre.vinculos.filter(
                ativo=True
            ).values_list('usuario__email', flat=False)
            # TODO: quando tiver subdepartamento definido, voltar aqui
            email_query_set_codae = Usuario.objects.filter(
                vinculos__perfil__nome__in=[COORDENADOR_GESTAO_ALIMENTACAO_TERCEIRIZADA,
                                            ADMINISTRADOR_GESTAO_ALIMENTACAO_TERCEIRIZADA]).values_list(
                'usuario__email', flat=False)
            email_lista = email_query_set_codae | email_query_set_dre

        elif self.ta_na_dre:
            email_query_set_dre = self.rastro_dre.vinculos.filter(
                ativo=True
            ).values_list('usuario__email', flat=False)
            email_lista = email_query_set_dre

        return [email for email in email_lista]

    @property
    def _partes_interessadas_dre_valida_ou_nao(self):
        email_query_set_escola = self.rastro_escola.vinculos.filter(
            ativo=True
        ).values_list('usuario__email', flat=True)
        return [email for email in email_query_set_escola]

    @property
    def _partes_interessadas_codae_autoriza_ou_nega(self):
        email_lista = []
        email_query_set_escola = self.rastro_escola.vinculos.filter(
            ativo=True
        ).values_list('usuario__email', flat=False)
        email_query_set_dre = self.rastro_dre.vinculos.filter(
            ativo=True
        ).values_list('usuario__email', flat=False)
        email_lista = email_query_set_escola | email_query_set_dre
        return [email for email in email_lista]

    @property
    def partes_interessadas_terceirizadas_tomou_ciencia(self):
        # TODO: definir partes interessadas
        return []

    @property
    def template_mensagem(self):
        raise NotImplementedError(
            'Deve criar um property que recupera o assunto e corpo mensagem desse objeto')

    def salvar_log_transicao(self, status_evento, usuario, **kwargs):
        raise NotImplementedError('Deve criar um método salvar_log_transicao')

    #
    # Esses hooks são chamados automaticamente após a
    # transition do status ser chamada.
    # Ex. >>> alimentacao_continua.inicia_fluxo(param1, param2, key1='val')
    #

    def _preenche_template_e_envia_email(self, assunto, titulo, user, partes_interessadas):
        template = 'fluxo_autorizar_negar_cancelar.html'
        dados_template = {'titulo': titulo, 'tipo_solicitacao': self.DESCRICAO,
                          'movimentacao_realizada': str(self.status), 'perfil_que_autorizou': user.nome}
        html = render_to_string(template, dados_template)
        envia_email_em_massa_task.delay(
            assunto=assunto,
            corpo='',
            emails=partes_interessadas,
            template='fluxo_autorizar_negar_cancelar.html',
            dados_template={'titulo': titulo, 'tipo_solicitacao': self.DESCRICAO,
                            'movimentacao_realizada': str(self.status), 'perfil_que_autorizou': user.nome},
            html=html
        )

    @xworkflows.after_transition('inicia_fluxo')
    def _inicia_fluxo_hook(self, *args, **kwargs):
        self.foi_solicitado_fora_do_prazo = self.prioridade in [
            'PRIORITARIO', 'LIMITE']
        self._salva_rastro_solicitacao()
        user = kwargs['user']
        self.salvar_log_transicao(status_evento=LogSolicitacoesUsuario.INICIO_FLUXO,
                                  usuario=user)

    @xworkflows.after_transition('dre_valida')
    def _dre_valida_hook(self, *args, **kwargs):
        user = kwargs['user']
        if user:
            assunto = '[SIGPAE] Status de solicitação - #' + self.id_externo
            titulo = 'Status de solicitação - #' + self.id_externo
            # manda email pra escola que solicitou de que a solicitacao foi
            # validada

            self.salvar_log_transicao(status_evento=LogSolicitacoesUsuario.DRE_VALIDOU,
                                      usuario=user)
            self._preenche_template_e_envia_email(
                assunto, titulo, user, self._partes_interessadas_dre_valida_ou_nao)

    @xworkflows.after_transition('dre_pede_revisao')
    def _dre_pede_revisao_hook(self, *args, **kwargs):
        user = kwargs['user']
        if user:
            assunto, corpo = self.template_mensagem
            self.salvar_log_transicao(status_evento=LogSolicitacoesUsuario.DRE_PEDIU_REVISAO,
                                      usuario=user)

    @xworkflows.after_transition('dre_nao_valida')
    def _dre_nao_valida_hook(self, *args, **kwargs):
        user = kwargs['user']
        justificativa = kwargs.get('justificativa', '')
        # manda email pra escola que solicitou de que a solicitacao NAO foi
        # validada
        if user:
            assunto = '[SIGPAE] Status de solicitação - #' + self.id_externo
            titulo = 'Status de solicitação - #' + self.id_externo
            self.salvar_log_transicao(status_evento=LogSolicitacoesUsuario.DRE_NAO_VALIDOU,
                                      justificativa=justificativa,
                                      usuario=user)
            self._preenche_template_e_envia_email(
                assunto, titulo, user, self._partes_interessadas_dre_valida_ou_nao)

    @xworkflows.after_transition('escola_revisa')
    def _escola_revisa_hook(self, *args, **kwargs):
        user = kwargs['user']
        if user:
            assunto, corpo = self.template_mensagem
            self.salvar_log_transicao(status_evento=LogSolicitacoesUsuario.ESCOLA_REVISOU,
                                      usuario=user)

    @xworkflows.after_transition('codae_questiona')
    def _codae_questiona_hook(self, *args, **kwargs):
        user = kwargs['user']
        justificativa = kwargs.get('justificativa', '')
        if user:
            assunto, corpo = self.template_mensagem
            self.salvar_log_transicao(status_evento=LogSolicitacoesUsuario.CODAE_QUESTIONOU,
                                      justificativa=justificativa,
                                      usuario=user)

    @xworkflows.before_transition('codae_autoriza_questionamento')
    @xworkflows.before_transition('codae_autoriza')
    def _codae_autoriza_hook_antes(self, *args, **kwargs):
        if (self.foi_solicitado_fora_do_prazo and
            self.status != PedidoAPartirDaEscolaWorkflow.TERCEIRIZADA_RESPONDEU_QUESTIONAMENTO):  # noqa #129
            raise xworkflows.InvalidTransitionError(
                f'CODAE não pode autorizar direto caso seja em cima da hora, deve questionar')

    @xworkflows.after_transition('codae_autoriza_questionamento')
    @xworkflows.after_transition('codae_autoriza')
    def _codae_autoriza_hook(self, *args, **kwargs):
        # manda email pra escola que solicitou e a DRE dela que validou de que
        # a solicitacao foi autorizada
        user = kwargs['user']
        justificativa = kwargs.get('justificativa', '')
        if user:
            assunto = '[SIGPAE] Status de solicitação - #' + self.id_externo
            titulo = 'Status de solicitação - #' + self.id_externo
            self.salvar_log_transicao(status_evento=LogSolicitacoesUsuario.CODAE_AUTORIZOU,
                                      usuario=user,
                                      justificativa=justificativa)
            self._preenche_template_e_envia_email(assunto, titulo, user,
                                                  self._partes_interessadas_codae_autoriza_ou_nega)

    @xworkflows.after_transition('codae_nega_questionamento')
    @xworkflows.after_transition('codae_nega')
    def _codae_recusou_hook(self, *args, **kwargs):
        user = kwargs['user']
        justificativa = kwargs.get('justificativa', '')
        # manda email pra escola que solicitou e a DRE dela que validou de que
        # a solicitacao NAO foi autorizada
        if user:
            assunto = '[SIGPAE] Status de solicitação - #' + self.id_externo
            titulo = 'Status de solicitação - #' + self.id_externo
            self.salvar_log_transicao(status_evento=LogSolicitacoesUsuario.CODAE_NEGOU,
                                      usuario=user,
                                      justificativa=justificativa)
            self._preenche_template_e_envia_email(assunto, titulo, user,
                                                  self._partes_interessadas_codae_autoriza_ou_nega)

    @xworkflows.after_transition('terceirizada_toma_ciencia')
    def _terceirizada_toma_ciencia_hook(self, *args, **kwargs):
        user = kwargs['user']
        if user:
            assunto, corpo = self.template_mensagem
            self.salvar_log_transicao(status_evento=LogSolicitacoesUsuario.TERCEIRIZADA_TOMOU_CIENCIA,
                                      usuario=user)

    @xworkflows.after_transition('terceirizada_responde_questionamento')
    def _terceirizada_responde_questionamento_hook(self, *args, **kwargs):
        user = kwargs['user']
        justificativa = kwargs.get('justificativa', '')
        resposta_sim_nao = kwargs.get('resposta_sim_nao', False)
        if user:
            assunto, corpo = self.template_mensagem
            self.salvar_log_transicao(status_evento=LogSolicitacoesUsuario.TERCEIRIZADA_RESPONDEU_QUESTIONAMENTO,
                                      justificativa=justificativa,
                                      resposta_sim_nao=resposta_sim_nao,
                                      usuario=user)

    class Meta:
        abstract = True


class FluxoAprovacaoPartindoDaDiretoriaRegional(xwf_models.WorkflowEnabled, models.Model):
    workflow_class = PedidoAPartirDaDiretoriaRegionalWorkflow
    status = xwf_models.StateField(workflow_class)
    DIAS_PARA_CANCELAR = 2

    rastro_escolas = models.ManyToManyField('escola.Escola',
                                            blank=True,
                                            related_name='%(app_label)s_%(class)s_rastro_escola',
                                            editable=False)
    rastro_dre = models.ForeignKey('escola.DiretoriaRegional',
                                   on_delete=models.DO_NOTHING,
                                   null=True,
                                   related_name='%(app_label)s_%(class)s_rastro_dre',
                                   blank=True,
                                   editable=False)
    rastro_lote = models.ForeignKey('escola.Lote',
                                    on_delete=models.DO_NOTHING,
                                    null=True,
                                    blank=True,
                                    related_name='%(app_label)s_%(class)s_rastro_lote',
                                    editable=False)
    rastro_terceirizada = models.ForeignKey('terceirizada.Terceirizada',
                                            on_delete=models.DO_NOTHING,
                                            null=True,
                                            blank=True,
                                            related_name='%(app_label)s_%(class)s_rastro_terceirizada',
                                            editable=False)

    def _salva_rastro_solicitacao(self):
        escolas = [i.escola for i in self.escolas_quantidades.all()]
        self.rastro_escolas.set(escolas)
        self.rastro_dre = self.diretoria_regional
        self.rastro_lote = self.lote
        self.rastro_terceirizada = self.lote.terceirizada
        self.save()

    def cancelar_pedido(self, user, justificativa=''):
        """O objeto que herdar de FluxoAprovacaoPartindoDaDiretoriaRegional, deve ter um property data.

        Atualmente o único pedido da DRE é o Solicitação kit lanche unificada
        Dado dias de antecedencia de prazo, verifica se pode e altera o estado
        """
        dia_antecedencia = datetime.date.today(
        ) + datetime.timedelta(days=self.DIAS_PARA_CANCELAR)
        data_do_evento = self.data
        if isinstance(data_do_evento, datetime.datetime):
            # TODO: verificar por que os models estao retornando datetime em
            # vez de date
            data_do_evento = data_do_evento.date()

        if (data_do_evento > dia_antecedencia) and (self.status != self.workflow_class.DRE_CANCELOU):
            self.status = self.workflow_class.DRE_CANCELOU
            self.salvar_log_transicao(status_evento=LogSolicitacoesUsuario.DRE_CANCELOU,
                                      usuario=user, justificativa=justificativa)
            self.save()
            # envia email para partes interessadas
            assunto = '[SIGPAE] Status de solicitação - #' + self.id_externo
            titulo = 'Status de solicitação - #' + self.id_externo
            self._preenche_template_e_envia_email(assunto, titulo, user,
                                                  self._partes_interessadas_cancelamento)

        elif self.status == self.workflow_class.DRE_CANCELOU:
            raise xworkflows.InvalidTransitionError('Já está cancelada')
        else:
            raise xworkflows.InvalidTransitionError(
                f'Só pode cancelar com no mínimo {self.DIAS_PARA_CANCELAR} dia(s) de antecedência')

    @property
    def pode_excluir(self):
        return self.status == self.workflow_class.RASCUNHO

    @property
    def ta_na_dre(self):
        return self.status in [self.workflow_class.CODAE_PEDIU_DRE_REVISAR,
                               self.workflow_class.RASCUNHO]

    @property
    def ta_na_codae(self):
        return self.status == self.workflow_class.CODAE_A_AUTORIZAR

    @property
    def ta_na_terceirizada(self):
        return self.status == self.workflow_class.CODAE_AUTORIZADO

    @property
    def _partes_interessadas_cancelamento(self):
        """Quando a dre cancela a sua solicitação, a codae deve ser avisados caso tenha chegado neles.

        Será retornada uma lista de emails para envio via celery.
        """
        if self.ta_na_codae:
            # TODO: quando tiver subdepartamento definido, voltar aqui
            email_query_set_codae = Usuario.objects.filter(
                vinculos__perfil__nome__in=[COORDENADOR_DIETA_ESPECIAL, ADMINISTRADOR_DIETA_ESPECIAL]).values_list(
                'usuario__email', flat=False)

            return [email for email in email_query_set_codae]

    @property
    def _partes_interessadas_codae_autoriza_ou_nega(self):
        email_query_set_dre = self.rastro_dre.vinculos.filter(
            ativo=True
        ).values_list('usuario__email', flat=False)
        return [email for email in email_query_set_dre]

    @property
    def partes_interessadas_inicio_fluxo(self):
        # TODO: definir partes interessadas
        return []

    @property
    def partes_interessadas_terceirizadas_tomou_ciencia(self):
        # TODO: definir partes interessadas
        return []

    @property
    def template_mensagem(self):
        raise NotImplementedError(
            'Deve criar um property que recupera o assunto e corpo mensagem desse objeto')

    def salvar_log_transicao(self, status_evento, usuario, **kwargs):
        raise NotImplementedError('Deve criar um método salvar_log_transicao')

    def _preenche_template_e_envia_email(self, assunto, titulo, user, partes_interessadas):
        template = 'fluxo_autorizar_negar_cancelar.html'
        dados_template = {'titulo': titulo, 'tipo_solicitacao': self.DESCRICAO,
                          'movimentacao_realizada': str(self.status), 'perfil_que_autorizou': user.nome}
        html = render_to_string(template, dados_template)
        envia_email_em_massa_task.delay(
            assunto=assunto,
            corpo='',
            emails=partes_interessadas,
            template='fluxo_autorizar_negar_cancelar.html',
            dados_template={'titulo': titulo, 'tipo_solicitacao': self.DESCRICAO,
                            'movimentacao_realizada': str(self.status), 'perfil_que_autorizou': user.nome},
            html=html
        )

    @xworkflows.after_transition('inicia_fluxo')
    def _inicia_fluxo_hook(self, *args, **kwargs):
        self.foi_solicitado_fora_do_prazo = self.prioridade in [
            'PRIORITARIO', 'LIMITE']
        user = kwargs['user']
        assunto, corpo = self.template_mensagem

        self.salvar_log_transicao(status_evento=LogSolicitacoesUsuario.INICIO_FLUXO,
                                  usuario=user)
        self._salva_rastro_solicitacao()

    @xworkflows.after_transition('codae_autoriza_questionamento')
    @xworkflows.after_transition('codae_autoriza')
    def _codae_autoriza_hook(self, *args, **kwargs):
        justificativa = kwargs.get('justificativa', '')
        user = kwargs['user']
        if user:
            assunto = '[SIGPAE] Status de solicitação - #' + self.id_externo
            titulo = 'Status de solicitação - #' + self.id_externo
            self.salvar_log_transicao(status_evento=LogSolicitacoesUsuario.CODAE_AUTORIZOU,
                                      usuario=user,
                                      justificativa=justificativa)
            self._preenche_template_e_envia_email(assunto, titulo, user,
                                                  self._partes_interessadas_codae_autoriza_ou_nega)

    @xworkflows.after_transition('codae_questiona')
    def _codae_questiona_hook(self, *args, **kwargs):
        user = kwargs['user']
        justificativa = kwargs.get('justificativa', '')
        if user:
            assunto, corpo = self.template_mensagem
            self.salvar_log_transicao(status_evento=LogSolicitacoesUsuario.CODAE_QUESTIONOU,
                                      justificativa=justificativa,
                                      usuario=user)

    @xworkflows.after_transition('terceirizada_toma_ciencia')
    def _terceirizada_toma_ciencia_hook(self, *args, **kwargs):
        user = kwargs['user']
        if user:
            assunto, corpo = self.template_mensagem
            self.salvar_log_transicao(status_evento=LogSolicitacoesUsuario.TERCEIRIZADA_TOMOU_CIENCIA,
                                      usuario=user)

    @xworkflows.after_transition('terceirizada_responde_questionamento')
    def _terceirizada_responde_questionamento_hook(self, *args, **kwargs):
        user = kwargs['user']
        justificativa = kwargs.get('justificativa', '')
        resposta_sim_nao = kwargs.get('resposta_sim_nao', False)
        if user:
            assunto, corpo = self.template_mensagem
            self.salvar_log_transicao(status_evento=LogSolicitacoesUsuario.TERCEIRIZADA_RESPONDEU_QUESTIONAMENTO,
                                      justificativa=justificativa,
                                      resposta_sim_nao=resposta_sim_nao,
                                      usuario=user)

    @xworkflows.after_transition('codae_nega_questionamento')
    @xworkflows.after_transition('codae_nega')
    def _codae_recusou_hook(self, *args, **kwargs):
        user = kwargs['user']
        justificativa = kwargs.get('justificativa', '')
        if user:
            assunto = '[SIGPAE] Status de solicitação - #' + self.id_externo
            titulo = 'Status de solicitação - #' + self.id_externo
            self.salvar_log_transicao(status_evento=LogSolicitacoesUsuario.CODAE_NEGOU,
                                      usuario=user,
                                      justificativa=justificativa)
            self._preenche_template_e_envia_email(assunto, titulo, user,
                                                  self._partes_interessadas_codae_autoriza_ou_nega)

    class Meta:
        abstract = True


class FluxoInformativoPartindoDaEscola(xwf_models.WorkflowEnabled, models.Model):
    workflow_class = InformativoPartindoDaEscolaWorkflow
    status = xwf_models.StateField(workflow_class)

    rastro_escola = models.ForeignKey('escola.Escola',
                                      on_delete=models.DO_NOTHING,
                                      null=True,
                                      blank=True,
                                      related_name='%(app_label)s_%(class)s_rastro_escola',
                                      editable=False)
    rastro_dre = models.ForeignKey('escola.DiretoriaRegional',
                                   on_delete=models.DO_NOTHING,
                                   null=True,
                                   related_name='%(app_label)s_%(class)s_rastro_dre',
                                   blank=True,
                                   editable=False)
    rastro_lote = models.ForeignKey('escola.Lote',
                                    on_delete=models.DO_NOTHING,
                                    null=True,
                                    blank=True,
                                    related_name='%(app_label)s_%(class)s_rastro_lote',
                                    editable=False)
    rastro_terceirizada = models.ForeignKey('terceirizada.Terceirizada',
                                            on_delete=models.DO_NOTHING,
                                            null=True,
                                            blank=True,
                                            related_name='%(app_label)s_%(class)s_rastro_terceirizada',
                                            editable=False)

    def _salva_rastro_solicitacao(self):
        self.rastro_escola = self.escola
        self.rastro_dre = self.escola.diretoria_regional
        self.rastro_lote = self.escola.lote
        self.rastro_terceirizada = self.escola.lote.terceirizada
        self.save()

    @property
    def pode_excluir(self):
        return self.status == self.workflow_class.RASCUNHO

    @property
    def partes_interessadas_informacao(self):
        # TODO: definir partes interessadas
        return []

    @property
    def partes_interessadas_terceirizadas_tomou_ciencia(self):
        # TODO: definir partes interessadas
        return []

    @property
    def template_mensagem(self):
        raise NotImplementedError(
            'Deve criar um property que recupera o assunto e corpo mensagem desse objeto')

    @xworkflows.after_transition('informa')
    def _informa_hook(self, *args, **kwargs):
        user = kwargs['user']
        assunto, corpo = self.template_mensagem
        self.salvar_log_transicao(status_evento=LogSolicitacoesUsuario.INICIO_FLUXO,
                                  usuario=user)
        self._salva_rastro_solicitacao()

    @xworkflows.after_transition('terceirizada_toma_ciencia')
    def _terceirizada_toma_ciencia_hook(self, *args, **kwargs):
        user = kwargs['user']
        if user:
            assunto, corpo = self.template_mensagem
            self.salvar_log_transicao(status_evento=LogSolicitacoesUsuario.TERCEIRIZADA_TOMOU_CIENCIA,
                                      usuario=user)

    class Meta:
        abstract = True


class FluxoDietaEspecialPartindoDaEscola(xwf_models.WorkflowEnabled, models.Model):
    workflow_class = DietaEspecialWorkflow
    status = xwf_models.StateField(workflow_class)

    rastro_escola = models.ForeignKey('escola.Escola',
                                      on_delete=models.DO_NOTHING,
                                      null=True,
                                      blank=True,
                                      related_name='%(app_label)s_%(class)s_rastro_escola',
                                      editable=False)
    rastro_dre = models.ForeignKey('escola.DiretoriaRegional',
                                   on_delete=models.DO_NOTHING,
                                   null=True,
                                   related_name='%(app_label)s_%(class)s_rastro_dre',
                                   blank=True,
                                   editable=False)
    rastro_lote = models.ForeignKey('escola.Lote',
                                    on_delete=models.DO_NOTHING,
                                    null=True,
                                    blank=True,
                                    related_name='%(app_label)s_%(class)s_rastro_lote',
                                    editable=False)
    rastro_terceirizada = models.ForeignKey('terceirizada.Terceirizada',
                                            on_delete=models.DO_NOTHING,
                                            null=True,
                                            blank=True,
                                            related_name='%(app_label)s_%(class)s_rastro_terceirizada',
                                            editable=False)

    def _salva_rastro_solicitacao(self):
        escola = self.criado_por.vinculo_atual.instituicao
        self.rastro_escola = escola
        self.rastro_dre = escola.diretoria_regional
        self.rastro_lote = escola.lote
        self.rastro_terceirizada = escola.lote.terceirizada
        self.save()

    def termina(self, usuario):
        if not self.ativo or self.status not in [self.workflow_class.CODAE_AUTORIZADO,
                                                 self.workflow_class.TERCEIRIZADA_TOMOU_CIENCIA,
                                                 self.workflow_class.ESCOLA_SOLICITOU_INATIVACAO,
                                                 self.workflow_class.CODAE_NEGOU_INATIVACAO]:
            raise xworkflows.InvalidTransitionError(
                'Só é permitido terminar dietas autorizadas e ativas')
        if self.data_termino is None:
            raise xworkflows.InvalidTransitionError(
                'Não pode terminar uma dieta sem data de término')
        if self.data_termino and self.data_termino > datetime.date.today():
            raise xworkflows.InvalidTransitionError(
                'Não pode terminar uma dieta antes da data')
        self.status = self.workflow_class.TERMINADA_AUTOMATICAMENTE_SISTEMA
        self.ativo = False
        self.salvar_log_transicao(status_evento=LogSolicitacoesUsuario.TERMINADA_AUTOMATICAMENTE_SISTEMA,
                                  usuario=usuario,
                                  justificativa='Atingiu data limite e foi terminada automaticamente')
        self.save()
        self._envia_email_termino()

    @property
    def _partes_interessadas_inicio_fluxo(self):
        """Quando a escola faz a solicitação, as pessoas da DRE são as partes interessadas.

        Será retornada uma lista de emails para envio via celery.
        """
        email_query_set = self.rastro_escola.vinculos.filter(
            ativo=True
        ).values_list('usuario__email', flat=False)
        return [email for email in email_query_set]

    @property
    def _partes_interessadas_termino(self):
        """Obtém endereços de email das partes interessadas num término de dieta especial.

        A dieta especial termina quando a data de término é atingida.
        São as partes interessadas:
            - A Escola solicitante
            - Nutricionistas CODAE
            - Terceirizada que tomou ciência (se aplicável)
        """
        email_query_set_escola = self.rastro_escola.vinculos.filter(
            ativo=True
        ).values_list('usuario__email')
        email_lista = [email for email in email_query_set_escola]
        email_query_set_codae = Usuario.objects.filter(
            vinculos__perfil__nome=COORDENADOR_DIETA_ESPECIAL).values_list(
            'email')
        email_lista += [email for email in email_query_set_codae]
        if self.rastro_terceirizada:
            email_query_set_terceirizada = self.rastro_terceirizada.vinculos.filter(
                ativo=True
            ).values_list('usuario__email', flat=False)
            email_lista += [email for email in email_query_set_terceirizada]
        return email_lista

    @property
    def _partes_interessadas_codae_autoriza_ou_nega(self):
        email_query_set_escola = self.rastro_escola.vinculos.filter(
            ativo=True
        ).values_list('usuario__email', flat=True)
        email_lista = [email for email in email_query_set_escola]
        if self.tipo_solicitacao != TIPO_SOLICITACAO_DIETA.get('COMUM'):
            if self.escola_destino.lote.terceirizada:
                email_query_set_terceirizada = self.escola_destino.lote.terceirizada.vinculos.filter(
                    ativo=True
                ).values_list('usuario__email', flat=True)
                email_lista += [email for email in email_query_set_terceirizada]
        return email_lista

    @property
    def partes_interessadas_terceirizadas_tomou_ciencia(self):
        # TODO: definir partes interessadas
        return []

    @property
    def template_mensagem(self):
        raise NotImplementedError(
            'Deve criar um property que recupera o assunto e corpo mensagem desse objeto')

    def _preenche_template_e_envia_email(self, assunto, titulo, user, partes_interessadas):
        template = 'fluxo_autorizar_negar_cancelar.html'
        dados_template = {'titulo': titulo, 'tipo_solicitacao': self.DESCRICAO,
                          'movimentacao_realizada': str(self.status), 'perfil_que_autorizou': user.nome}
        html = render_to_string(template, dados_template)
        envia_email_em_massa_task.delay(
            assunto=assunto,
            corpo='',
            emails=partes_interessadas,
            template='fluxo_autorizar_negar_cancelar.html',
            dados_template={'titulo': titulo, 'tipo_solicitacao': self.DESCRICAO,
                            'movimentacao_realizada': str(self.status), 'perfil_que_autorizou': user.nome},
            html=html
        )

    @xworkflows.after_transition('inicia_fluxo')
    def _inicia_fluxo_hook(self, *args, **kwargs):
        self._salva_rastro_solicitacao()
        user = kwargs['user']
        self.salvar_log_transicao(status_evento=LogSolicitacoesUsuario.INICIO_FLUXO,
                                  usuario=user)

    @xworkflows.after_transition('cancelar_pedido')
    def _cancelar_pedido_hook(self, *args, **kwargs):
        user = kwargs['user']
        justificativa = kwargs['justificativa']
        self.salvar_log_transicao(status_evento=LogSolicitacoesUsuario.ESCOLA_CANCELOU,
                                  usuario=user,
                                  justificativa=justificativa)

    @xworkflows.after_transition('codae_nega')
    def _codae_nega_hook(self, *args, **kwargs):
        user = kwargs['user']
        assunto = '[SIGPAE] Status de solicitação - #' + self.id_externo
        titulo = 'Status de solicitação - #' + self.id_externo
        self.salvar_log_transicao(status_evento=LogSolicitacoesUsuario.CODAE_NEGOU,
                                  usuario=user)
        self._preenche_template_e_envia_email(assunto, titulo, user,
                                              self._partes_interessadas_codae_autoriza_ou_nega)

    @xworkflows.after_transition('codae_autoriza')
    def _codae_autoriza_hook(self, *args, **kwargs):
        user = kwargs['user']
        assunto = '[SIGPAE] Status de solicitação - #' + self.id_externo
        titulo = 'Status de solicitação - #' + self.id_externo
        self.salvar_log_transicao(status_evento=LogSolicitacoesUsuario.CODAE_AUTORIZOU,
                                  usuario=user)
        self._preenche_template_e_envia_email(assunto, titulo, user,
                                              self._partes_interessadas_codae_autoriza_ou_nega)

    @xworkflows.after_transition('inicia_fluxo_inativacao')
    def _inicia_fluxo_inativacao_hook(self, *args, **kwargs):
        user = kwargs['user']
        justificativa = kwargs.get('justificativa', '')
        self.salvar_log_transicao(status_evento=LogSolicitacoesUsuario.INICIO_FLUXO_INATIVACAO,
                                  usuario=user,
                                  justificativa=justificativa)

    @xworkflows.after_transition('codae_autoriza_inativacao')
    def _codae_autoriza_inativacao_hook(self, *args, **kwargs):
        user = kwargs['user']
        self.salvar_log_transicao(status_evento=LogSolicitacoesUsuario.CODAE_AUTORIZOU_INATIVACAO,
                                  usuario=user)

    @xworkflows.after_transition('codae_nega_inativacao')
    def _codae_nega_inativacao_hook(self, *args, **kwargs):
        user = kwargs['user']
        justificativa = kwargs.get('justificativa', '')
        self.salvar_log_transicao(status_evento=LogSolicitacoesUsuario.CODAE_NEGOU_INATIVACAO,
                                  usuario=user,
                                  justificativa=justificativa)

    @xworkflows.after_transition('terceirizada_toma_ciencia_inativacao')
    def _terceirizada_toma_ciencia_inativacao_hook(self, *args, **kwargs):
        user = kwargs['user']
        if user:
            self.salvar_log_transicao(status_evento=LogSolicitacoesUsuario.TERCEIRIZADA_TOMOU_CIENCIA_INATIVACAO,
                                      usuario=user)

    @xworkflows.after_transition('terceirizada_toma_ciencia')
    def _terceirizada_toma_ciencia_hook(self, *args, **kwargs):
        user = kwargs['user']
        if user:
            self.salvar_log_transicao(status_evento=LogSolicitacoesUsuario.TERCEIRIZADA_TOMOU_CIENCIA,
                                      usuario=user)

    def _envia_email_termino(self):
        assunto = f'[SIGPAE] Prazo de fornecimento de dieta encerrado - Solicitação #{self.id_externo}'
        template = 'fluxo_dieta_especial_termina.html'
        dados_template = {
            'eol_aluno': self.aluno.codigo_eol,
            'nome_aluno': self.aluno.nome
        }
        html = render_to_string(template, dados_template)
        envia_email_em_massa_task.delay(
            assunto=assunto,
            corpo='',
            emails=self._partes_interessadas_termino,
            html=html
        )

    class Meta:
        abstract = True


class ReclamacaoProdutoWorkflow(xwf_models.Workflow):
    log_model = ''  # Disable logging to database

    AGUARDANDO_AVALIACAO = 'AGUARDANDO_AVALIACAO'  # INICIO
    AGUARDANDO_RESPOSTA_TERCEIRIZADA = 'AGUARDANDO_RESPOSTA_TERCEIRIZADA'
    RESPONDIDO_TERCEIRIZADA = 'RESPONDIDO_TERCEIRIZADA'
    CODAE_ACEITOU = 'CODAE_ACEITOU'
    CODAE_RECUSOU = 'CODAE_RECUSOU'
    CODAE_RESPONDEU = 'CODAE_RESPONDEU'

    states = (
        (AGUARDANDO_AVALIACAO, 'Aguardando avaliação da CODAE'),
        (AGUARDANDO_RESPOSTA_TERCEIRIZADA, 'Aguardando resposta da terceirizada'),
        (RESPONDIDO_TERCEIRIZADA, 'Respondido pela terceirizada'),
        (CODAE_ACEITOU, 'CODAE aceitou'),
        (CODAE_RECUSOU, 'CODAE recusou'),
        (CODAE_RESPONDEU, 'CODAE respondeu ao reclamante'),
    )

    transitions = (
        ('codae_questiona', AGUARDANDO_AVALIACAO, AGUARDANDO_RESPOSTA_TERCEIRIZADA),
        ('terceirizada_responde', AGUARDANDO_RESPOSTA_TERCEIRIZADA,
         RESPONDIDO_TERCEIRIZADA),
        ('codae_aceita', [AGUARDANDO_AVALIACAO,
                          RESPONDIDO_TERCEIRIZADA], CODAE_ACEITOU),
        ('codae_recusa', [AGUARDANDO_AVALIACAO,
                          RESPONDIDO_TERCEIRIZADA], CODAE_RECUSOU),
        ('codae_responde', [AGUARDANDO_AVALIACAO,
                            RESPONDIDO_TERCEIRIZADA], CODAE_RESPONDEU),
    )

    initial_state = AGUARDANDO_AVALIACAO


class FluxoReclamacaoProduto(xwf_models.WorkflowEnabled, models.Model):
    workflow_class = ReclamacaoProdutoWorkflow
    status = xwf_models.StateField(workflow_class)

    def _partes_interessadas_suspensao_por_reclamacao(self):
        queryset = Usuario.objects.filter(
            vinculos__ativo=True,
            vinculos__perfil__nome__in=[
                'ADMINISTRADOR_ESCOLA',
                'DIRETOR',
                'DIRETOR CEI',
                'ADMINISTRADOR_TERCEIRIZADA',
                'NUTRI_ADMIN_RESPONSAVEL',
                'COORDENADOR_SUPERVISAO_NUTRICAO',
                'ADMINISTRADOR_SUPERVISAO_NUTRICAO']
        )
        return [usuario.email for usuario in queryset]

    def _envia_email_recusa_reclamacao(self, log_recusa):
        html = render_to_string(
            template_name='produto_codae_recusou_reclamacao.html',
            context={
                'titulo': 'Reclamação recusada',
                'reclamacao': self,
                'log_recusa': log_recusa
            }
        )
        envia_email_unico_task.delay(
            assunto='[SIGPAE] Reclamação recusada',
            email=self.criado_por.email,
            corpo='',
            html=html
        )

    def _envia_email_resposta_reclamacao(self, log_resposta):
        html = render_to_string(
            template_name='produto_codae_responde_reclamacao.html',
            context={
                'titulo': 'Resposta a reclamação realizada',
                'reclamacao': self,
                'log_resposta': log_resposta
            }
        )
        envia_email_unico_task.delay(
            assunto='[SIGPAE] Resposta a reclamação realizada',
            email=self.criado_por.email,
            corpo='',
            html=html
        )

    def _envia_email_aceite_reclamacao(self, log_aceite):
        html = render_to_string(
            template_name='produto_codae_aceitou_reclamacao.html',
            context={
                'titulo': 'Produto suspenso por reclamação',
                'reclamacao': self,
                'log_aceite': log_aceite
            }
        )
        envia_email_em_massa_task.delay(
            assunto='[SIGPAE] Produto suspenso por reclamação',
            emails=self._partes_interessadas_suspensao_por_reclamacao(),
            corpo='',
            html=html
        )

    @xworkflows.after_transition('codae_aceita')
    def _codae_aceita_hook(self, *args, **kwargs):
        log_aceite = self.salvar_log_transicao(
            status_evento=LogSolicitacoesUsuario.CODAE_AUTORIZOU_RECLAMACAO,
            **kwargs)
        self._envia_email_aceite_reclamacao(log_aceite)

    @xworkflows.after_transition('codae_recusa')
    def _codae_recusa_hook(self, *args, **kwargs):
        log_recusa = self.salvar_log_transicao(
            status_evento=LogSolicitacoesUsuario.CODAE_RECUSOU_RECLAMACAO,
            **kwargs)
        self._envia_email_recusa_reclamacao(log_recusa)

    @xworkflows.after_transition('codae_questiona')
    def _codae_questiona_hook(self, *args, **kwargs):
        self.salvar_log_transicao(
            status_evento=LogSolicitacoesUsuario.CODAE_QUESTIONOU_TERCEIRIZADA,
            **kwargs)

    @xworkflows.after_transition('codae_responde')
    def _codae_responde_hook(self, *args, **kwargs):
        log_resposta = self.salvar_log_transicao(
            status_evento=LogSolicitacoesUsuario.CODAE_RESPONDEU_RECLAMACAO,
            **kwargs)
        self._envia_email_resposta_reclamacao(log_resposta)

    @xworkflows.after_transition('terceirizada_responde')
    def _terceirizada_responde_hook(self, *args, **kwargs):
        self.salvar_log_transicao(
            status_evento=LogSolicitacoesUsuario.TERCEIRIZADA_RESPONDEU_RECLAMACAO,
            **kwargs)

    class Meta:
        abstract = True


class SolicitacaoCadastroProdutoWorkflow(xwf_models.Workflow):
    log_model = ''  # Disable logging to database

    AGUARDANDO_CONFIRMACAO = 'AGUARDANDO_CONFIRMACAO'  # INICIO
    CONFIRMADA = 'CONFIRMADA'

    states = (
        (AGUARDANDO_CONFIRMACAO, 'Aguardando confirmação'),
        (CONFIRMADA, 'Confirmada'),
    )

    transitions = (
        ('terceirizada_atende_solicitacao', AGUARDANDO_CONFIRMACAO, CONFIRMADA),
    )

    initial_state = AGUARDANDO_CONFIRMACAO


class FluxoSolicitacaoCadastroProduto(xwf_models.WorkflowEnabled, models.Model):
    workflow_class = SolicitacaoCadastroProdutoWorkflow
    status = xwf_models.StateField(workflow_class)

    def _partes_interessadas_solicitacao_cadastro_produto(self):
        queryset = Usuario.objects.filter(
            vinculos__ativo=True,
            vinculos__perfil__nome__in=[
                'ADMINISTRADOR_GESTAO_PRODUTO',
                'COORDENADOR_GESTAO_PRODUTO',
                'COORDENADOR_DIETA_ESPECIAL']
        )
        return [usuario.email for usuario in queryset]

    def _envia_email_solicitacao_realizada(self):

        html = render_to_string(
            template_name='dieta_especial_solicitou_cadastro_produto.html',
            context={
                'titulo': 'Solicitação de cadastro de novo produto realizada',
                'solicitacao': self
            }
        )

        assunto = '[SIGPAE] Solicitação de cadastro de novo produto realizada'
        emails = self._partes_interessadas_solicitacao_cadastro_produto()
        emails.append(self.terceirizada.contatos.last().email)
        corpo = ''

        envia_email_em_massa_task.delay(
            assunto=assunto,
            emails=emails,
            corpo=corpo,
            html=html
        )
