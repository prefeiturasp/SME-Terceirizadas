import pytest
from freezegun import freeze_time
from model_mommy import mommy
from rest_framework.exceptions import ValidationError

from ...cardapio.api.serializers.serializers_create import InversaoCardapioSerializerCreate
from ...cardapio.models import InversaoCardapio

pytestmark = pytest.mark.django_db


@freeze_time('2019-10-14')
def test_inversao_serializer_validators(inversao_card_params):
    data_de, data_para = inversao_card_params
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

    data_de, data_para = inversao_card_params
    serializer_obj = InversaoCardapioSerializerCreate(context={'request': FakeObject})
    cardapio_de = mommy.make('cardapio.Cardapio', data=data_de)
    cardapio_para = mommy.make('cardapio.Cardapio', data=data_para)
    tipo_ue = mommy.make('escola.TipoUnidadeEscolar', cardapios=[cardapio_de, cardapio_para])
    escola = mommy.make('escola.Escola', tipo_unidade=tipo_ue)

    validated_data = dict(data_de=data_de, data_para=data_para, escola=escola)
    response = serializer_obj.create(validated_data=validated_data)
    assert isinstance(response, InversaoCardapio)

    assert response.cardapio_de.data == data_de
    assert response.cardapio_para.data == data_para
    assert response.escola == escola
