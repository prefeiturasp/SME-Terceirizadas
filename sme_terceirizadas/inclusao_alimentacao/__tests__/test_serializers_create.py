import pytest
from freezegun import freeze_time
from model_mommy import mommy

from sme_terceirizadas.inclusao_alimentacao.api.serializers.serializers_create import \
    InclusaoAlimentacaoContinuaCreationSerializer
from sme_terceirizadas.inclusao_alimentacao.models import InclusaoAlimentacaoContinua

pytestmark = pytest.mark.django_db


@freeze_time('2019-10-15')
def test_inclusao_continua_serializer_validators(inclusao_alimentacao_continua_parametros):
    class FakeObject(object):
        user = mommy.make('perfil.Usuario')

    data_inicial, data_final, dias_semana = inclusao_alimentacao_continua_parametros
    attrs = dict(data_inicial=data_inicial, data_final=data_final)
    quantidades_por_periodo = []
    for i in range(4):
        qtd = mommy.make('QuantidadePorPeriodo')
        quantidades_por_periodo.append(dict(numero_alunos=qtd.numero_alunos,
                                            periodo_escolar=qtd.periodo_escolar,
                                            tipos_alimentacao=[]))

    serializer_obj = InclusaoAlimentacaoContinuaCreationSerializer(context={'request': FakeObject})
    resp_inicial = serializer_obj.validate_data_inicial(data_inicial)
    resp_final = serializer_obj.validate_data_final(data_final)
    resp_qtd_periodo = serializer_obj.validate_quantidades_periodo(quantidades_por_periodo)
    resp_attrs = serializer_obj.validate(attrs=attrs)

    assert resp_inicial == data_inicial
    assert resp_final == data_final
    assert resp_attrs == attrs
    assert resp_qtd_periodo == quantidades_por_periodo


@freeze_time('2019-10-15')
def test_inclusao_continua_serializer_creators(inclusao_alimentacao_continua_parametros):
    class FakeObject(object):
        user = mommy.make('perfil.Usuario')

    escola = mommy.make('escola.Escola')
    motivo = mommy.make('MotivoInclusaoContinua')
    data_inicial, data_final, dias_semana = inclusao_alimentacao_continua_parametros
    quantidades_por_periodo = []
    for i in range(4):
        qtd = mommy.make('QuantidadePorPeriodo')
        quantidades_por_periodo.append(dict(numero_alunos=qtd.numero_alunos,
                                            periodo_escolar=qtd.periodo_escolar,
                                            tipos_alimentacao=[]))

    serializer_obj = InclusaoAlimentacaoContinuaCreationSerializer(context={'request': FakeObject})
    validated_data = dict(quantidades_periodo=quantidades_por_periodo,
                          data_inicial=data_inicial,
                          data_final=data_final,
                          dias_semana=dias_semana,
                          escola=escola,
                          motivo=motivo)
    validated_data_update = dict(quantidades_periodo=quantidades_por_periodo[:3],
                                 data_inicial=data_inicial,
                                 data_final=data_final,
                                 dias_semana=dias_semana,
                                 escola=escola,
                                 motivo=motivo)

    inclusao_continua_obj = serializer_obj.create(validated_data=validated_data)
    assert isinstance(inclusao_continua_obj, InclusaoAlimentacaoContinua)
    assert inclusao_continua_obj.data_inicial == data_inicial
    assert inclusao_continua_obj.data_final == data_final
    assert inclusao_continua_obj.escola == escola
    assert inclusao_continua_obj.motivo == motivo
    assert inclusao_continua_obj.quantidades_periodo.count() == 4
    assert inclusao_continua_obj.criado_por == FakeObject.user

    inclusao_continua_obj_updated = serializer_obj.update(instance=inclusao_continua_obj,
                                                          validated_data=validated_data_update)
    assert isinstance(inclusao_continua_obj_updated, InclusaoAlimentacaoContinua)
    assert inclusao_continua_obj.quantidades_periodo.count() == 3
