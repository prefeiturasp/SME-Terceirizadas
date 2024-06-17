from unittest.mock import Mock

from django.contrib.admin.sites import AdminSite

from sme_terceirizadas.dados_comuns.behaviors import PerfilDiretorSupervisao
from sme_terceirizadas.imr.admin import (
    ParametrizacaoOcorrenciaAdmin,
    PerfisFilter,
    TipoOcorrenciaAdmin,
    TipoPenalidadeAdmin,
)
from sme_terceirizadas.imr.models import (
    ParametrizacaoOcorrencia,
    TipoOcorrencia,
    TipoPenalidade,
)


def test_tipo_penalidade_admin(
    client_autenticado_vinculo_coordenador_supervisao_nutricao, tipo_penalidade_factory
):
    client, usuario = client_autenticado_vinculo_coordenador_supervisao_nutricao

    tipo_penalidade = tipo_penalidade_factory()
    tipo_penalidade_admin = TipoPenalidadeAdmin(
        model=TipoPenalidade, admin_site=AdminSite()
    )
    tipo_penalidade_admin.save_model(
        obj=tipo_penalidade, request=Mock(user=usuario), form=None, change=None
    )
    assert tipo_penalidade.criado_por == usuario


def test_tipo_ocorrencia_admin(
    client_autenticado_vinculo_coordenador_supervisao_nutricao, tipo_ocorrencia_factory
):
    client, usuario = client_autenticado_vinculo_coordenador_supervisao_nutricao

    tipo_ocorrencia = tipo_ocorrencia_factory()
    tipo_ocorrencia_admin = TipoOcorrenciaAdmin(
        model=TipoOcorrencia, admin_site=AdminSite()
    )
    tipo_ocorrencia_admin.save_model(
        obj=tipo_ocorrencia, request=Mock(user=usuario), form=None, change=None
    )
    assert tipo_ocorrencia.criado_por == usuario


def test_perfis_filter_admin(
    client_autenticado_vinculo_coordenador_supervisao_nutricao,
    parametrizacao_ocorrencia_factory,
):
    client, usuario = client_autenticado_vinculo_coordenador_supervisao_nutricao

    parametrizacao_ocorrencia_factory.create(tipo_ocorrencia__perfis=["DIRETOR"])
    parametrizacao_ocorrencia_factory.create(tipo_ocorrencia__perfis=["SUPERVISAO"])

    perfis_filter = PerfisFilter(
        Mock(user=usuario),
        {"perfis": "Diretor"},
        PerfilDiretorSupervisao,
        ParametrizacaoOcorrenciaAdmin,
    )
    queryset = perfis_filter.queryset(
        Mock(user=usuario), ParametrizacaoOcorrencia.objects.all()
    )
    assert queryset.count() == 1

    perfis_filter = PerfisFilter(
        Mock(user=usuario),
        {"perfis": "Supervisao"},
        PerfilDiretorSupervisao,
        ParametrizacaoOcorrenciaAdmin,
    )
    queryset = perfis_filter.queryset(
        Mock(user=usuario), ParametrizacaoOcorrencia.objects.all()
    )
    assert queryset.count() == 1

    perfis_filter = PerfisFilter(
        Mock(user=usuario),
        {"perfis": "Tudo"},
        PerfilDiretorSupervisao,
        ParametrizacaoOcorrenciaAdmin,
    )
    queryset = perfis_filter.queryset(
        Mock(user=usuario), ParametrizacaoOcorrencia.objects.all()
    )
    assert queryset.count() == 2


def test_parametrizacao_ocorrencia_admin(
    client_autenticado_vinculo_coordenador_supervisao_nutricao,
    parametrizacao_ocorrencia_factory,
):
    edital_numero = "78/SME/2016"
    perfis = ["DIRETOR"]
    parametrizacao_ocorrencia = parametrizacao_ocorrencia_factory.create(
        tipo_ocorrencia__edital__numero=edital_numero, tipo_ocorrencia__perfis=perfis
    )
    parametrizacao_ocorrencia_admin = ParametrizacaoOcorrenciaAdmin(
        model=ParametrizacaoOcorrencia, admin_site=AdminSite()
    )
    assert (
        parametrizacao_ocorrencia_admin.edital(parametrizacao_ocorrencia)
        == edital_numero
    )
    assert parametrizacao_ocorrencia_admin.perfis(parametrizacao_ocorrencia) == perfis
