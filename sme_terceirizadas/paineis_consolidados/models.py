import datetime
import operator

from django.db import models
from django.db.models import Q

from ..dados_comuns.behaviors import TemIdentificadorExternoAmigavel, TemPrioridade
from ..dados_comuns.constants import DAQUI_A_SETE_DIAS, DAQUI_A_TRINTA_DIAS
from ..dados_comuns.fluxo_status import (
    InformativoPartindoDaEscolaWorkflow,
    PedidoAPartirDaDiretoriaRegionalWorkflow,
    PedidoAPartirDaEscolaWorkflow
)
from ..dados_comuns.models import LogSolicitacoesUsuario


class SolicitacoesDestaSemanaManager(models.Manager):
    def get_queryset(self):
        hoje = datetime.date.today()
        data_limite_inicial = hoje
        data_limite_final = hoje + datetime.timedelta(7)
        return super(SolicitacoesDestaSemanaManager, self).get_queryset(
        ).filter(data_evento__range=(data_limite_inicial, data_limite_final))


class SolicitacoesDesteMesManager(models.Manager):
    def get_queryset(self):
        hoje = datetime.date.today()
        data_limite_inicial = hoje
        data_limite_final = hoje + datetime.timedelta(31)
        return super(SolicitacoesDesteMesManager, self).get_queryset(
        ).filter(data_evento__range=(data_limite_inicial, data_limite_final))


class MoldeConsolidado(models.Model, TemPrioridade, TemIdentificadorExternoAmigavel):
    TODOS = 'TODOS'
    ALT_CARDAPIO = 'ALT_CARDAPIO'
    INV_CARDAPIO = 'INV_CARDAPIO'
    INC_ALIMENTA = 'INC_ALIMENTA'
    INC_ALIMENTA_CONTINUA = 'INC_ALIMENTA_CONTINUA'
    KIT_LANCHE_AVULSA = 'KIT_LANCHE_AVULSA'
    SUSP_ALIMENTACAO = 'SUSP_ALIMENTACAO'
    KIT_LANCHE_UNIFICADA = 'KIT_LANCHE_UNIFICADA'

    uuid = models.UUIDField(editable=False)
    data_evento = models.DateField()
    criado_em = models.DateTimeField()
    lote_nome = models.CharField(max_length=50)
    dre_nome = models.CharField(max_length=200)
    escola_nome = models.CharField(max_length=200)
    terceirizada_nome = models.CharField(max_length=200)

    lote_uuid = models.UUIDField(editable=False)
    escola_uuid = models.UUIDField(editable=False)
    dre_uuid = models.UUIDField(editable=False)
    terceirizada_uuid = models.UUIDField(editable=False)

    tipo_doc = models.CharField(max_length=30)
    desc_doc = models.CharField(max_length=50)
    data_log = models.DateTimeField()
    status_evento = models.PositiveSmallIntegerField()
    numero_alunos = models.PositiveSmallIntegerField()
    status_atual = models.CharField(max_length=32)

    objects = models.Manager()
    filtro_7_dias = SolicitacoesDestaSemanaManager()
    filtro_30_dias = SolicitacoesDesteMesManager()

    @classmethod
    def get_pendentes_autorizacao(cls, **kwargs):
        raise NotImplementedError('Precisa implementar')

    @classmethod
    def get_autorizados(cls, **kwargs):
        raise NotImplementedError('Precisa implementar')

    @classmethod
    def get_negados(cls, **kwargs):
        raise NotImplementedError('Precisa implementar')

    @classmethod
    def get_cancelados(cls, **kwargs):
        raise NotImplementedError('Precisa implementar')

    @property
    def data(self):
        return self.data_evento

    @classmethod
    def _get_manager(cls, kwargs):
        filtro = kwargs.get('filtro')
        manager = cls.objects
        if filtro == DAQUI_A_SETE_DIAS:
            manager = cls.filtro_7_dias
        elif filtro == DAQUI_A_TRINTA_DIAS:
            manager = cls.filtro_30_dias
        return manager

    class Meta:
        managed = False
        db_table = 'solicitacoes_consolidadas'
        abstract = True


class SolicitacoesCODAE(MoldeConsolidado):

    #
    # Filtros padrão
    #

    @classmethod
    def get_pendentes_autorizacao(cls, **kwargs):
        manager = cls._get_manager(kwargs)
        return manager.filter(
            status_evento__in=[LogSolicitacoesUsuario.DRE_VALIDOU,
                               LogSolicitacoesUsuario.TERCEIRIZADA_RESPONDEU_QUESTIONAMENTO],
            status_atual__in=[PedidoAPartirDaEscolaWorkflow.TERCEIRIZADA_RESPONDEU_QUESTIONAMENTO,
                              PedidoAPartirDaEscolaWorkflow.DRE_VALIDADO,
                              PedidoAPartirDaDiretoriaRegionalWorkflow.CODAE_A_AUTORIZAR]
        ).distinct().order_by('-data_log')

    @classmethod
    def get_autorizados(cls, **kwargs):
        return cls.objects.filter(
            status_evento__in=[LogSolicitacoesUsuario.CODAE_AUTORIZOU,
                               LogSolicitacoesUsuario.TERCEIRIZADA_TOMOU_CIENCIA],
            status_atual__in=[PedidoAPartirDaEscolaWorkflow.CODAE_AUTORIZADO,
                              PedidoAPartirDaEscolaWorkflow.TERCEIRIZADA_TOMOU_CIENCIA]
        ).distinct().order_by('-data_log')

    @classmethod
    def get_negados(cls, **kwargs):
        return cls.objects.filter(
            status_evento=LogSolicitacoesUsuario.CODAE_NEGOU,
            status_atual=PedidoAPartirDaEscolaWorkflow.CODAE_NEGOU_PEDIDO
        ).distinct().order_by('-data_log')

    @classmethod
    def get_cancelados(cls, **kwargs):
        return cls.objects.filter(
            status_evento__in=[LogSolicitacoesUsuario.DRE_CANCELOU,
                               LogSolicitacoesUsuario.ESCOLA_CANCELOU],
            status_atual__in=[PedidoAPartirDaEscolaWorkflow.ESCOLA_CANCELOU,
                              PedidoAPartirDaDiretoriaRegionalWorkflow.DRE_CANCELOU],
        ).distinct().order_by('-data_log')

    #
    # Filtros consolidados
    #

    @classmethod
    def resumo_totais_mes(cls, **kwargs):
        hoje = datetime.date.today()
        mes_passado = datetime.date(year=hoje.year, month=hoje.month, day=1) - datetime.timedelta(days=1)
        query_set = cls.objects.filter(
            criado_em__date__year=hoje.year,
            criado_em__date__month=hoje.month,
        )
        query_set_mes_passado = cls.objects.filter(
            criado_em__date__year=mes_passado.year,
            criado_em__date__month=mes_passado.month,
        )

        return dict(
            total_autorizados=cls._conta_autorizados(query_set),
            total_negados=cls._conta_negados(query_set),
            total_cancelados=cls._conta_cancelados(query_set),
            total_pendentes=cls._conta_pendentes(query_set),

            total_autorizados_mes_passado=cls._conta_autorizados(query_set_mes_passado),
            total_negados_mes_passado=cls._conta_negados(query_set_mes_passado),
            total_cancelados_mes_passado=cls._conta_cancelados(query_set_mes_passado),
            total_pendentes_mes_passado=cls._conta_pendentes(query_set_mes_passado)
        )

    @staticmethod
    def _conta_autorizados(query_set):
        return query_set.filter(status_atual__in=[
            PedidoAPartirDaEscolaWorkflow.CODAE_AUTORIZADO,
            PedidoAPartirDaEscolaWorkflow.TERCEIRIZADA_TOMOU_CIENCIA
        ]).count()

    @staticmethod
    def _conta_negados(query_set):
        return query_set.filter(status_atual=PedidoAPartirDaEscolaWorkflow.CODAE_NEGOU_PEDIDO).count()

    @staticmethod
    def _conta_cancelados(query_set):
        return query_set.filter(status_atual=PedidoAPartirDaEscolaWorkflow.ESCOLA_CANCELOU).count()

    @staticmethod
    def _conta_pendentes(query_set):
        return query_set.filter(status_atual__in=[
            PedidoAPartirDaEscolaWorkflow.TERCEIRIZADA_RESPONDEU_QUESTIONAMENTO,
            PedidoAPartirDaEscolaWorkflow.DRE_VALIDADO,
            PedidoAPartirDaDiretoriaRegionalWorkflow.CODAE_A_AUTORIZAR]).count()


class SolicitacoesEscola(MoldeConsolidado):

    #
    # Filtros padrão
    #

    @classmethod
    def get_pendentes_autorizacao(cls, **kwargs):
        escola_uuid = kwargs.get('escola_uuid')
        return cls.objects.filter(
            escola_uuid=escola_uuid
        ).filter(
            status_atual__in=[PedidoAPartirDaEscolaWorkflow.DRE_A_VALIDAR,
                              PedidoAPartirDaEscolaWorkflow.DRE_VALIDADO,
                              PedidoAPartirDaEscolaWorkflow.CODAE_QUESTIONADO,
                              PedidoAPartirDaEscolaWorkflow.TERCEIRIZADA_RESPONDEU_QUESTIONAMENTO,
                              InformativoPartindoDaEscolaWorkflow.INFORMADO],
            status_evento__in=[LogSolicitacoesUsuario.INICIO_FLUXO,
                               LogSolicitacoesUsuario.DRE_VALIDOU,
                               LogSolicitacoesUsuario.CODAE_QUESTIONOU,
                               LogSolicitacoesUsuario.TERCEIRIZADA_RESPONDEU_QUESTIONAMENTO]
        ).distinct().order_by('-data_log')

    @classmethod
    def get_autorizados(cls, **kwargs):
        escola_uuid = kwargs.get('escola_uuid')
        return cls.objects.filter(
            escola_uuid=escola_uuid
        ).filter(
            Q(status_evento=LogSolicitacoesUsuario.CODAE_AUTORIZOU,
              status_atual=PedidoAPartirDaEscolaWorkflow.CODAE_AUTORIZADO) |  # noqa W504
            Q(status_evento=LogSolicitacoesUsuario.TERCEIRIZADA_TOMOU_CIENCIA,
              status_atual=PedidoAPartirDaEscolaWorkflow.TERCEIRIZADA_TOMOU_CIENCIA)
        ).distinct().order_by('-data_log')

    @classmethod
    def get_negados(cls, **kwargs):
        escola_uuid = kwargs.get('escola_uuid')
        return cls.objects.filter(
            status_evento=LogSolicitacoesUsuario.CODAE_NEGOU,
            status_atual=PedidoAPartirDaEscolaWorkflow.CODAE_NEGOU_PEDIDO,
            escola_uuid=escola_uuid
        ).distinct().order_by('-data_log')

    @classmethod
    def get_cancelados(cls, **kwargs):
        escola_uuid = kwargs.get('escola_uuid')
        return cls.objects.filter(
            status_evento=LogSolicitacoesUsuario.ESCOLA_CANCELOU,
            status_atual=PedidoAPartirDaEscolaWorkflow.ESCOLA_CANCELOU,
            escola_uuid=escola_uuid
        ).distinct().order_by('-data_log')

    #
    # Filtros consolidados
    #

    @classmethod
    def get_solicitacoes_ano_corrente(cls, **kwargs):
        """Usado para geração do gráfico."""
        escola_uuid = kwargs.get('escola_uuid')
        return cls.objects.filter(
            escola_uuid=escola_uuid,
            data_evento__year=datetime.date.today().year
            # TODO: devemos filtrar por data do evento ou data em que foi criado?
        ).distinct().order_by('-data_log').values('data_evento__month', 'desc_doc')

    @classmethod  # noqa C901
    def filtros_escola(cls, **kwargs):
        # TODO: melhorar esse código, está complexo.
        escola_uuid = kwargs.get('escola_uuid')
        data_inicial = kwargs.get('data_inicial', None)
        data_final = kwargs.get('data_final', None)
        tipo_solicitacao = kwargs.get('tipo_solicitacao', cls.TODOS)
        status_solicitacao = kwargs.get('status_solicitacao', cls.TODOS)

        query_set = cls.objects.filter(
            escola_uuid=escola_uuid
        )
        if data_inicial and data_final:
            query_set = query_set.filter(criado_em__date__range=(data_inicial, data_final))
        if tipo_solicitacao != cls.TODOS:
            query_set = query_set.filter(tipo_doc=tipo_solicitacao)

        if status_solicitacao != cls.TODOS:
            # AUTORIZADOS|NEGADOS|CANCELADOS|EM_ANDAMENTO|TODOS
            if status_solicitacao == 'AUTORIZADOS':
                query_set = query_set.filter(status_atual__in=[
                    PedidoAPartirDaEscolaWorkflow.CODAE_AUTORIZADO,
                    PedidoAPartirDaEscolaWorkflow.TERCEIRIZADA_TOMOU_CIENCIA
                ])
            elif status_solicitacao == 'NEGADOS':
                query_set = query_set.filter(status_atual=PedidoAPartirDaEscolaWorkflow.CODAE_NEGOU_PEDIDO)
            elif status_solicitacao == 'CANCELADOS':
                query_set = query_set.filter(status_atual=PedidoAPartirDaEscolaWorkflow.ESCOLA_CANCELOU)
            elif status_solicitacao == 'EM_ANDAMENTO':
                query_set = query_set.filter(status_atual__in=[
                    PedidoAPartirDaEscolaWorkflow.DRE_VALIDADO,
                    PedidoAPartirDaEscolaWorkflow.DRE_A_VALIDAR,
                    PedidoAPartirDaEscolaWorkflow.CODAE_QUESTIONADO,
                    PedidoAPartirDaEscolaWorkflow.TERCEIRIZADA_RESPONDEU_QUESTIONAMENTO
                ])

        return query_set.order_by('-criado_em')

    @staticmethod
    def _conta_autorizados(query_set):
        return query_set.filter(status_atual__in=[
            PedidoAPartirDaEscolaWorkflow.CODAE_AUTORIZADO,
            PedidoAPartirDaEscolaWorkflow.TERCEIRIZADA_TOMOU_CIENCIA
        ]).count()

    @staticmethod
    def _conta_negados(query_set):
        return query_set.filter(status_atual=PedidoAPartirDaEscolaWorkflow.CODAE_NEGOU_PEDIDO).count()

    @staticmethod
    def _conta_cancelados(query_set):
        return query_set.filter(status_atual=PedidoAPartirDaEscolaWorkflow.ESCOLA_CANCELOU).count()

    @staticmethod
    def _conta_pendentes(query_set):
        return query_set.filter(status_atual__in=[
            PedidoAPartirDaEscolaWorkflow.DRE_VALIDADO,
            PedidoAPartirDaEscolaWorkflow.DRE_A_VALIDAR,
            PedidoAPartirDaEscolaWorkflow.CODAE_QUESTIONADO,
            PedidoAPartirDaEscolaWorkflow.TERCEIRIZADA_RESPONDEU_QUESTIONAMENTO
        ]).count()

    @classmethod
    def resumo_totais_mes(cls, **kwargs):
        escola_uuid = kwargs.get('escola_uuid')
        hoje = datetime.date.today()
        mes_passado = datetime.date(year=hoje.year, month=hoje.month, day=1) - datetime.timedelta(days=1)
        query_set = cls.objects.filter(
            escola_uuid=escola_uuid,
            criado_em__date__year=hoje.year,
            criado_em__date__month=hoje.month,

        )
        query_set_mes_passado = cls.objects.filter(
            escola_uuid=escola_uuid,
            criado_em__date__year=mes_passado.year,
            criado_em__date__month=mes_passado.month,

        )

        return dict(
            total_autorizados=cls._conta_autorizados(query_set),
            total_negados=cls._conta_negados(query_set),
            total_cancelados=cls._conta_cancelados(query_set),
            total_pendentes=cls._conta_pendentes(query_set),

            total_autorizados_mes_passado=cls._conta_autorizados(query_set_mes_passado),
            total_negados_mes_passado=cls._conta_negados(query_set_mes_passado),
            total_cancelados_mes_passado=cls._conta_cancelados(query_set_mes_passado),
            total_pendentes_mes_passado=cls._conta_pendentes(query_set_mes_passado)
        )


class SolicitacoesDRE(MoldeConsolidado):

    #
    # Filtros padrão
    #

    @classmethod
    def get_pendentes_autorizacao(cls, **kwargs):
        dre_uuid = kwargs.get('dre_uuid')
        return cls.objects.filter(
            status_atual__in=[PedidoAPartirDaDiretoriaRegionalWorkflow.CODAE_A_AUTORIZAR,
                              PedidoAPartirDaEscolaWorkflow.CODAE_QUESTIONADO,
                              PedidoAPartirDaEscolaWorkflow.TERCEIRIZADA_RESPONDEU_QUESTIONAMENTO,
                              PedidoAPartirDaEscolaWorkflow.DRE_VALIDADO],
            status_evento__in=[LogSolicitacoesUsuario.DRE_VALIDOU,
                               LogSolicitacoesUsuario.INICIO_FLUXO,
                               LogSolicitacoesUsuario.CODAE_QUESTIONOU,
                               LogSolicitacoesUsuario.TERCEIRIZADA_RESPONDEU_QUESTIONAMENTO],
            dre_uuid=dre_uuid
        ).distinct().order_by('-data_log')

    @classmethod
    def get_pendentes_validacao(cls, **kwargs):
        dre_uuid = kwargs.get('dre_uuid')
        manager = cls._get_manager(kwargs)
        return manager.filter(
            status_atual=PedidoAPartirDaEscolaWorkflow.DRE_A_VALIDAR,
            status_evento=LogSolicitacoesUsuario.INICIO_FLUXO,
            dre_uuid=dre_uuid
        ).distinct().order_by('-data_log')

    @classmethod
    def get_autorizados(cls, **kwargs):
        dre_uuid = kwargs.get('dre_uuid')
        return cls.objects.filter(
            status_evento__in=[LogSolicitacoesUsuario.CODAE_AUTORIZOU,
                               LogSolicitacoesUsuario.TERCEIRIZADA_TOMOU_CIENCIA],
            status_atual__in=[PedidoAPartirDaDiretoriaRegionalWorkflow.CODAE_AUTORIZADO,
                              PedidoAPartirDaDiretoriaRegionalWorkflow.TERCEIRIZADA_TOMOU_CIENCIA,
                              PedidoAPartirDaEscolaWorkflow.CODAE_AUTORIZADO,
                              PedidoAPartirDaEscolaWorkflow.TERCEIRIZADA_TOMOU_CIENCIA],
            dre_uuid=dre_uuid
        ).distinct().order_by('-data_log')

    @classmethod
    def get_negados(cls, **kwargs):
        dre_uuid = kwargs.get('dre_uuid')
        return cls.objects.filter(
            status_evento__in=[LogSolicitacoesUsuario.CODAE_NEGOU,
                               LogSolicitacoesUsuario.DRE_NAO_VALIDOU],
            status_atual__in=[PedidoAPartirDaDiretoriaRegionalWorkflow.CODAE_NEGOU_PEDIDO,
                              PedidoAPartirDaEscolaWorkflow.CODAE_NEGOU_PEDIDO,
                              PedidoAPartirDaEscolaWorkflow.DRE_NAO_VALIDOU_PEDIDO_ESCOLA, ],
            dre_uuid=dre_uuid
        ).distinct().order_by('-data_log')

    @classmethod
    def get_cancelados(cls, **kwargs):
        dre_uuid = kwargs.get('dre_uuid')
        return cls.objects.filter(
            status_evento__in=[LogSolicitacoesUsuario.DRE_CANCELOU,
                               LogSolicitacoesUsuario.ESCOLA_CANCELOU],
            status_atual__in=[PedidoAPartirDaDiretoriaRegionalWorkflow.DRE_CANCELOU,
                              PedidoAPartirDaEscolaWorkflow.ESCOLA_CANCELOU],
            dre_uuid=dre_uuid
        ).distinct().order_by('-data_log')

    #
    # Filtros  consolidados
    #

    @classmethod
    def resumo_totais_mes(cls, **kwargs):
        dre_uuid = kwargs.get('dre_uuid')
        hoje = datetime.date.today()
        mes_passado = datetime.date(year=hoje.year, month=hoje.month, day=1) - datetime.timedelta(days=1)
        query_set = cls.objects.filter(
            escola_uuid=dre_uuid,
            criado_em__date__year=hoje.year,
            criado_em__date__month=hoje.month,

        )
        query_set_mes_passado = cls.objects.filter(
            escola_uuid=dre_uuid,
            criado_em__date__year=mes_passado.year,
            criado_em__date__month=mes_passado.month,

        )

        return dict(
            total_autorizados=cls._conta_autorizados(query_set),
            total_negados=cls._conta_negados(query_set),
            total_cancelados=cls._conta_cancelados(query_set),
            total_pendentes=cls._conta_pendentes(query_set),

            total_autorizados_mes_passado=cls._conta_autorizados(query_set_mes_passado),
            total_negados_mes_passado=cls._conta_negados(query_set_mes_passado),
            total_cancelados_mes_passado=cls._conta_cancelados(query_set_mes_passado),
            total_pendentes_mes_passado=cls._conta_pendentes(query_set_mes_passado)
        )

    @staticmethod
    def _conta_autorizados(query_set):
        return query_set.filter(status_atual__in=[
            PedidoAPartirDaEscolaWorkflow.CODAE_AUTORIZADO,
            PedidoAPartirDaEscolaWorkflow.TERCEIRIZADA_TOMOU_CIENCIA
        ]).count()

    @staticmethod
    def _conta_negados(query_set):
        return query_set.filter(status_atual=PedidoAPartirDaEscolaWorkflow.CODAE_NEGOU_PEDIDO).count()

    @staticmethod
    def _conta_cancelados(query_set):
        return query_set.filter(status_atual=PedidoAPartirDaEscolaWorkflow.ESCOLA_CANCELOU).count()

    @staticmethod
    def _conta_pendentes(query_set):
        return query_set.filter(status_atual__in=[
            PedidoAPartirDaEscolaWorkflow.DRE_VALIDADO,
            PedidoAPartirDaEscolaWorkflow.DRE_A_VALIDAR,
            PedidoAPartirDaEscolaWorkflow.CODAE_QUESTIONADO,
            PedidoAPartirDaEscolaWorkflow.TERCEIRIZADA_RESPONDEU_QUESTIONAMENTO
        ]).count()


# TODO: voltar quando tiver o Rastro implementado
class SolicitacoesTerceirizada(MoldeConsolidado):

    @classmethod
    def get_questionamentos(cls, **kwargs):
        terceirizada_uuid = kwargs.get('terceirizada_uuid')
        s = cls.objects.filter(
            terceirizada_uuid=terceirizada_uuid,
            status_atual=PedidoAPartirDaEscolaWorkflow.CODAE_QUESTIONADO,
            status_evento=LogSolicitacoesUsuario.CODAE_QUESTIONOU
        )
        return sorted(s, key=operator.attrgetter('data_log'), reverse=True)

    @classmethod
    def get_pendentes_autorizacao(cls, **kwargs):
        terceirizada_uuid = kwargs.get('terceirizada_uuid')
        s = cls.objects.filter(
            terceirizada_uuid=terceirizada_uuid,
            status_atual__in=[PedidoAPartirDaDiretoriaRegionalWorkflow.CODAE_A_AUTORIZAR,
                              PedidoAPartirDaEscolaWorkflow.CODAE_QUESTIONADO,
                              PedidoAPartirDaEscolaWorkflow.TERCEIRIZADA_RESPONDEU_QUESTIONAMENTO,
                              PedidoAPartirDaEscolaWorkflow.DRE_VALIDADO],
            status_evento__in=[LogSolicitacoesUsuario.DRE_VALIDOU,
                               LogSolicitacoesUsuario.INICIO_FLUXO,
                               LogSolicitacoesUsuario.CODAE_QUESTIONOU,
                               LogSolicitacoesUsuario.TERCEIRIZADA_RESPONDEU_QUESTIONAMENTO],
        ).distinct('uuid')
        return sorted(s, key=operator.attrgetter('data_log'), reverse=True)

    @classmethod
    def get_autorizados(cls, **kwargs):
        terceirizada_uuid = kwargs.get('terceirizada_uuid')
        return cls.objects.filter(
            status_evento__in=[LogSolicitacoesUsuario.CODAE_AUTORIZOU,
                               LogSolicitacoesUsuario.TERCEIRIZADA_TOMOU_CIENCIA],
            status_atual__in=[PedidoAPartirDaEscolaWorkflow.CODAE_AUTORIZADO,
                              PedidoAPartirDaEscolaWorkflow.TERCEIRIZADA_TOMOU_CIENCIA],
            terceirizada_uuid=terceirizada_uuid
        ).distinct().order_by('-data_log')

    @classmethod
    def get_negados(cls, **kwargs):
        terceirizada_uuid = kwargs.get('terceirizada_uuid')
        return cls.objects.filter(
            status_evento=LogSolicitacoesUsuario.CODAE_NEGOU,
            status_atual=PedidoAPartirDaEscolaWorkflow.CODAE_NEGOU_PEDIDO,
            terceirizada_uuid=terceirizada_uuid
        ).distinct().order_by('-data_log')

    @classmethod
    def get_cancelados(cls, **kwargs):
        terceirizada_uuid = kwargs.get('terceirizada_uuid')
        return cls.objects.filter(
            status_evento__in=[LogSolicitacoesUsuario.DRE_CANCELOU,
                               LogSolicitacoesUsuario.ESCOLA_CANCELOU],
            status_atual__in=[PedidoAPartirDaEscolaWorkflow.ESCOLA_CANCELOU,
                              PedidoAPartirDaDiretoriaRegionalWorkflow.DRE_CANCELOU],
            terceirizada_uuid=terceirizada_uuid
        ).order_by('-data_log').distinct()

    @classmethod
    def get_pendentes_ciencia(cls, **kwargs):
        terceirizada_uuid = kwargs.get('terceirizada_uuid')
        manager = cls._get_manager(kwargs)
        return manager.filter(
            status_atual__in=[PedidoAPartirDaDiretoriaRegionalWorkflow.CODAE_AUTORIZADO,
                              PedidoAPartirDaEscolaWorkflow.CODAE_AUTORIZADO,
                              PedidoAPartirDaEscolaWorkflow.CODAE_QUESTIONADO,
                              InformativoPartindoDaEscolaWorkflow.INFORMADO],
            status_evento__in=[LogSolicitacoesUsuario.CODAE_AUTORIZOU,
                               LogSolicitacoesUsuario.INICIO_FLUXO],
            terceirizada_uuid=terceirizada_uuid
        ).distinct('uuid')
