from typing import Type

from django.db.models import QuerySet
from django_filters.rest_framework import FilterSet
from rest_framework.request import Request
from rest_framework.serializers import ModelSerializer

from sme_terceirizadas.dados_comuns.constants import (
    ADMINISTRADOR_EMPRESA,
    COORDENADOR_CODAE_DILOG_LOGISTICA,
    COORDENADOR_GESTAO_PRODUTO,
    DILOG_CRONOGRAMA,
    DILOG_DIRETORIA,
    DILOG_QUALIDADE,
    DINUTRE_DIRETORIA,
    USUARIO_EMPRESA,
)
from sme_terceirizadas.dados_comuns.fluxo_status import (
    CronogramaAlteracaoWorkflow,
    DocumentoDeRecebimentoWorkflow,
    FichaTecnicaDoProdutoWorkflow,
    LayoutDeEmbalagemWorkflow,
)
from sme_terceirizadas.pre_recebimento.models.cronograma import (
    SolicitacaoAlteracaoCronograma,
)


class BaseServiceDashboard:
    STATUS_POR_PERFIL = {}

    def __init__(
        self,
        original_queryset: QuerySet,
        filter_class: Type[FilterSet],
        serializer_class: Type[ModelSerializer],
        request: Request,
    ) -> None:
        """
        Service Base que deve ser extendido para lidar com perfis e os diferentes status dos cards dos dashboards.

        Na sua implementação concreta do Service, sobreescreva o dicionário STATUS_POR_PERFIL com um mapeamento
        dos perfils e os respectivos status dos cards desejados.

        Exemplo:

        STATUS_POR_PERFIL = {
            PERFIL_A: [
                'EM_ANALISE',
                'APROVADO',
                'REPROVADO',
            ],
            PERFIL_B: [
                'EM_ANALISE',
                'SOLICITADO_CORRECAO',
            ],
            PERFIL_C: [
                'APROVADO',
                'REPROVADO',
            ],
        }
        """
        self.original_queryset = original_queryset
        self.filter_class = filter_class
        self.serializer_class = serializer_class
        self.request = request

    @classmethod
    def get_dashboard_status(cls, user) -> list:
        perfil = user.vinculo_atual.perfil.nome

        if perfil not in cls.STATUS_POR_PERFIL:
            raise ValueError("Perfil não existe")

        return cls.STATUS_POR_PERFIL[perfil]

    def get_dados_dashboard(self) -> list:
        lista_status_ver_mais = self.request.query_params.getlist("status", None)
        offset = int(self.request.query_params.get("offset", 0))
        limit = int(self.request.query_params.get("limit", 6))

        filtered_queryset = self.filter_class(
            self.request.query_params, self.original_queryset
        ).qs

        if lista_status_ver_mais:
            dados = self._get_dados_ver_mais(
                filtered_queryset, lista_status_ver_mais, offset, limit
            )

        else:
            dados = self._get_dados_cards(filtered_queryset, offset, limit)

        return dados

    def _get_dados_ver_mais(self, queryset_base, lista_status_ver_mais, offset, limit):
        qs = queryset_base.filter(status__in=lista_status_ver_mais)
        dados = {
            "status": lista_status_ver_mais,
            "total": len(qs),
            "dados": self.serializer_class(qs[offset : offset + limit], many=True).data,
        }

        return dados

    def _get_dados_cards(self, queryset_base, offset, limit):
        dados = []
        for status_perfil in self.get_dashboard_status(self.request.user):
            status_perfil_list = [status_perfil]
            qs = queryset_base.filter(status__in=status_perfil_list)
            dados.append(
                {
                    "status": status_perfil,
                    "dados": self.serializer_class(
                        qs[offset : offset + limit], many=True
                    ).data,
                }
            )

        return dados


class ServiceDashboardSolicitacaoAlteracaoCronogramaProfiles(BaseServiceDashboard):
    STATUS_POR_PERFIL = {
        DINUTRE_DIRETORIA: [
            CronogramaAlteracaoWorkflow.CRONOGRAMA_CIENTE,
            CronogramaAlteracaoWorkflow.APROVADO_DINUTRE,
            CronogramaAlteracaoWorkflow.REPROVADO_DINUTRE,
            CronogramaAlteracaoWorkflow.ALTERACAO_ENVIADA_FORNECEDOR,
            CronogramaAlteracaoWorkflow.FORNECEDOR_CIENTE,
        ],
        DILOG_DIRETORIA: [
            CronogramaAlteracaoWorkflow.APROVADO_DINUTRE,
            CronogramaAlteracaoWorkflow.REPROVADO_DINUTRE,
            CronogramaAlteracaoWorkflow.APROVADO_DILOG,
            CronogramaAlteracaoWorkflow.REPROVADO_DILOG,
            CronogramaAlteracaoWorkflow.ALTERACAO_ENVIADA_FORNECEDOR,
            CronogramaAlteracaoWorkflow.FORNECEDOR_CIENTE,
        ],
        DILOG_CRONOGRAMA: [
            CronogramaAlteracaoWorkflow.EM_ANALISE,
            CronogramaAlteracaoWorkflow.APROVADO_DILOG,
            CronogramaAlteracaoWorkflow.REPROVADO_DILOG,
            CronogramaAlteracaoWorkflow.ALTERACAO_ENVIADA_FORNECEDOR,
            CronogramaAlteracaoWorkflow.FORNECEDOR_CIENTE,
        ],
        COORDENADOR_CODAE_DILOG_LOGISTICA: [
            CronogramaAlteracaoWorkflow.EM_ANALISE,
            CronogramaAlteracaoWorkflow.APROVADO_DILOG,
            CronogramaAlteracaoWorkflow.REPROVADO_DILOG,
            CronogramaAlteracaoWorkflow.ALTERACAO_ENVIADA_FORNECEDOR,
            CronogramaAlteracaoWorkflow.FORNECEDOR_CIENTE,
        ],
    }


class ServiceDashboardLayoutEmbalagem(BaseServiceDashboard):
    STATUS_POR_PERFIL = {
        COORDENADOR_CODAE_DILOG_LOGISTICA: [
            LayoutDeEmbalagemWorkflow.ENVIADO_PARA_ANALISE,
            LayoutDeEmbalagemWorkflow.APROVADO,
            LayoutDeEmbalagemWorkflow.SOLICITADO_CORRECAO,
        ],
        DILOG_QUALIDADE: [
            LayoutDeEmbalagemWorkflow.ENVIADO_PARA_ANALISE,
            LayoutDeEmbalagemWorkflow.APROVADO,
            LayoutDeEmbalagemWorkflow.SOLICITADO_CORRECAO,
        ],
        COORDENADOR_GESTAO_PRODUTO: [
            LayoutDeEmbalagemWorkflow.ENVIADO_PARA_ANALISE,
            LayoutDeEmbalagemWorkflow.APROVADO,
            LayoutDeEmbalagemWorkflow.SOLICITADO_CORRECAO,
        ],
    }


class ServiceDashboardDocumentosDeRecebimento(BaseServiceDashboard):
    STATUS_POR_PERFIL = {
        DILOG_QUALIDADE: [
            DocumentoDeRecebimentoWorkflow.ENVIADO_PARA_ANALISE,
            DocumentoDeRecebimentoWorkflow.APROVADO,
            DocumentoDeRecebimentoWorkflow.ENVIADO_PARA_CORRECAO,
        ],
        COORDENADOR_CODAE_DILOG_LOGISTICA: [
            DocumentoDeRecebimentoWorkflow.ENVIADO_PARA_ANALISE,
            DocumentoDeRecebimentoWorkflow.APROVADO,
            DocumentoDeRecebimentoWorkflow.ENVIADO_PARA_CORRECAO,
        ],
    }


class ServiceDashboardFichaTecnica(BaseServiceDashboard):
    STATUS_POR_PERFIL = {
        COORDENADOR_GESTAO_PRODUTO: [
            FichaTecnicaDoProdutoWorkflow.ENVIADA_PARA_ANALISE,
        ],
        COORDENADOR_CODAE_DILOG_LOGISTICA: [
            FichaTecnicaDoProdutoWorkflow.ENVIADA_PARA_ANALISE,
        ],
    }


class ServiceQuerysetAlteracaoCronograma:
    STATUS_PRIORITARIO = {
        ADMINISTRADOR_EMPRESA: [
            CronogramaAlteracaoWorkflow.ALTERACAO_ENVIADA_FORNECEDOR,
        ],
        USUARIO_EMPRESA: [
            CronogramaAlteracaoWorkflow.ALTERACAO_ENVIADA_FORNECEDOR,
        ],
        DILOG_CRONOGRAMA: [
            CronogramaAlteracaoWorkflow.EM_ANALISE,
        ],
        DILOG_DIRETORIA: [
            CronogramaAlteracaoWorkflow.APROVADO_DINUTRE,
            CronogramaAlteracaoWorkflow.REPROVADO_DINUTRE,
        ],
        DINUTRE_DIRETORIA: [
            CronogramaAlteracaoWorkflow.CRONOGRAMA_CIENTE,
        ],
    }

    def __init__(
        self,
        request: Request,
    ) -> None:
        self.request = request

    @classmethod
    def get_dashboard_status(self, user) -> list:
        perfil = user.vinculo_atual.perfil.nome

        if perfil not in self.STATUS_PRIORITARIO:
            raise ValueError("Perfil não existe")

        return self.STATUS_PRIORITARIO[perfil]

    def get_queryset(self):
        user = self.request.user
        lista_status = self.get_dashboard_status(user)
        q1 = SolicitacaoAlteracaoCronograma.objects.filter(
            status__in=lista_status,
        ).order_by("-criado_em")
        q2 = SolicitacaoAlteracaoCronograma.objects.exclude(
            status__in=lista_status,
        ).order_by("-criado_em")

        if user.eh_fornecedor:
            q1 = q1.filter(cronograma__empresa=user.vinculo_atual.instituicao)
            q2 = q2.filter(cronograma__empresa=user.vinculo_atual.instituicao)

        return q1.union(q2, all=True)
