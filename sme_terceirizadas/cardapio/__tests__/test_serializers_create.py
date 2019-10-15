import pytest
from freezegun import freeze_time
from model_mommy import mommy
from rest_framework.exceptions import ValidationError

from ...cardapio.api.serializers.serializers_create import InversaoCardapioSerializerCreate, \
    AlteracaoCardapioSerializerCreate
from ...cardapio.models import InversaoCardapio

pytestmark = pytest.mark.django_db


@freeze_time('2019-10-14')
def test_inversao_serializer_validators(inversao_card_params):
    data_de, data_para, _, _ = inversao_card_params
    serializer_obj = InversaoCardapioSerializerCreate()
    cardapio_de = mommy.make('cardapio.Cardapio', data=data_de)
    cardapio_para = mommy.make('cardapio.Cardapio', data=data_para)
    tipo_ue = mommy.make('escola.TipoUnidadeEscolar', cardapios=[cardapio_de, cardapio_para])
    escola = mommy.make('escola.Escola', tipo_unidade=tipo_ue)
    attrs = dict(data_de=data_de, data_para=data_para, escola=escola)

    response_de = serializer_obj.validate_data_de(data_de=data_de)
    response_para = serializer_obj.validate_data_para(data_para=data_para)
    response_geral = serializer_obj.validate(attrs=attrs)
    assert response_de == data_de
    assert response_para == data_para
    assert response_geral == attrs


@freeze_time('2019-10-14')
def test_inversao_serializer_validators_case_error(inversao_card_params_error):
    data_de, data_para = inversao_card_params_error
    serializer_obj = InversaoCardapioSerializerCreate()
    cardapio_de = mommy.make('cardapio.Cardapio', data=data_de)
    cardapio_para = mommy.make('cardapio.Cardapio', data=data_para)
    tipo_ue = mommy.make('escola.TipoUnidadeEscolar', cardapios=[cardapio_de, cardapio_para])
    escola = mommy.make('escola.Escola', tipo_unidade=tipo_ue)
    attrs = dict(data_de=data_de, data_para=data_para, escola=escola)

    error_regex = r'(Não pode ser no passado|Inversão de dia de cardapio deve ser solicitada no ano corrente|Diferença entre as datas não pode ultrapassar de 60 dias|Data de cardápio para troca é superior a data de inversão)'  # noqa E501
    with pytest.raises(ValidationError, match=error_regex):
        response_de = serializer_obj.validate_data_de(data_de=data_de)
        response_para = serializer_obj.validate_data_para(data_para=data_para)
        response_geral = serializer_obj.validate(attrs=attrs)
        assert response_de == data_de
        assert response_para == data_para
        assert response_geral == attrs


@freeze_time('2019-10-14')
def test_inversao_serializer_creators(inversao_card_params):
    class FakeObject(object):
        user = mommy.make('perfil.Usuario')

    data_de_cria, data_para, data_de_atualiza, data_para_atualiza = inversao_card_params
    serializer_obj = InversaoCardapioSerializerCreate(context={'request': FakeObject})

    cardapio1 = mommy.make('cardapio.Cardapio', data=data_de_cria)
    cardapio2 = mommy.make('cardapio.Cardapio', data=data_para)
    cardapio3 = mommy.make('cardapio.Cardapio', data=data_de_atualiza)
    cardapio4 = mommy.make('cardapio.Cardapio', data=data_para_atualiza)

    tipo_ue = mommy.make('escola.TipoUnidadeEscolar', cardapios=[cardapio1, cardapio2, cardapio3, cardapio4])
    escola1 = mommy.make('escola.Escola', tipo_unidade=tipo_ue)
    escola2 = mommy.make('escola.Escola', tipo_unidade=tipo_ue)

    validated_data_create = dict(data_de=data_de_cria, data_para=data_para, escola=escola1)
    validated_data_update = dict(data_de=data_de_atualiza, data_para=data_para_atualiza, escola=escola2)

    inversao_cardapio = serializer_obj.create(validated_data=validated_data_create)
    assert isinstance(inversao_cardapio, InversaoCardapio)

    assert inversao_cardapio.cardapio_de.data == data_de_cria
    assert inversao_cardapio.cardapio_para.data == data_para
    assert inversao_cardapio.escola == escola1

    instance = serializer_obj.update(instance=inversao_cardapio, validated_data=validated_data_update)
    assert isinstance(instance, InversaoCardapio)
    assert inversao_cardapio.cardapio_de.data == data_de_atualiza
    assert inversao_cardapio.cardapio_para.data == data_para_atualiza
    assert inversao_cardapio.escola == escola2


@freeze_time('2019-10-15')
def test_alteracao_cardapio_validators(alteracao_card_params):
    class FakeObject(object):
        user = mommy.make('perfil.Usuario')

    data_inicial, data_final = alteracao_card_params

    serializer_obj = AlteracaoCardapioSerializerCreate(context={'request': FakeObject})
    alteracao = mommy.make('cardapio.AlteracaoCardapio', data_inicial=data_inicial, data_final=data_final)

    alimentacao1 = mommy.make('cardapio.TipoAlimentacao')
    alimentacao2 = mommy.make('cardapio.TipoAlimentacao')
    alimentacao3 = mommy.make('cardapio.TipoAlimentacao')
    alimentacao4 = mommy.make('cardapio.TipoAlimentacao')
    alimentacao5 = mommy.make('cardapio.TipoAlimentacao')

    alimentacao1.substituicoes.set([alimentacao2, alimentacao4])
    alimentacao2.substituicoes.set([alimentacao3, alimentacao5])
    alimentacao3.substituicoes.set([alimentacao1, alimentacao4])
    alimentacao4.substituicoes.set([alimentacao3, alimentacao1])
    alimentacao5.substituicoes.set([alimentacao2, alimentacao4])

    substituicoes = []
    substituicoes_dict = []
    for substituicao in range(4):
        sub_obj = mommy.make('cardapio.SubstituicoesAlimentacaoNoPeriodoEscolar',
                             tipo_alimentacao_de=alimentacao1,
                             tipo_alimentacao_para=alimentacao4)
        substituicoes.append(sub_obj)
        substituicoes_dict.append(dict(tipo_alimentacao_de=alimentacao1, tipo_alimentacao_para=alimentacao4))
    alteracao.substituicoes.set(substituicoes)

    resp_dt_inicial = serializer_obj.validate_data_inicial(data_inicial=data_inicial)
    resp_substicuicoes = serializer_obj.validate_substituicoes(substituicoes=substituicoes_dict)
    assert resp_dt_inicial == data_inicial
    assert resp_substicuicoes == substituicoes_dict
