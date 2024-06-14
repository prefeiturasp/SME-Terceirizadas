from unittest.mock import Mock

from django.contrib.admin.sites import AdminSite

from sme_terceirizadas.imr.admin import TipoOcorrenciaAdmin, TipoPenalidadeAdmin
from sme_terceirizadas.imr.models import TipoOcorrencia, TipoPenalidade


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
