import datetime
import random

import pytest
from model_mommy import mommy

from ..api.serializers.serializers_create_cei import (
    FaixaEtariaSolicitacaoKitLancheCEIAvulsaCreateSerializer,
    SolicitacaoKitLancheCEIAvulsaCreationSerializer
)


@pytest.mark.django_db
def test_faixa_etaria_kit_lanche_cei_serializer():
    faixa_etaria = mommy.make('escola.FaixaEtaria')
    solic = mommy.make('kit_lanche.SolicitacaoKitLancheCEIAvulsa')
    data = {
        'solicitacao_kit_lanche_avulsa': solic.uuid,
        'faixa_etaria': faixa_etaria.uuid,
        'quantidade': 42
    }
    serializer = FaixaEtariaSolicitacaoKitLancheCEIAvulsaCreateSerializer(data=data)

    assert serializer.is_valid()


@pytest.mark.django_db
def test_kit_lanche_cei_avulsa_serializer_create():
    class FakeObject(object):
        user = mommy.make('perfil.Usuario')

    alunos = mommy.make('escola.Aluno', _quantity=4)
    alunos_com_dieta = [aluno.codigo_eol for aluno in alunos]

    escola = mommy.make('escola.Escola')
    data = datetime.date(2020, 9, 1)
    local = 'Tão-tão distante'

    kits_lanche = mommy.make('kit_lanche.KitLanche', _quantity=2)
    kits_escolhidos = [kit.uuid for kit in kits_lanche]
    tempo_passeio = 1

    faixas_etarias = mommy.make('escola.FaixaEtaria', _quantity=5)
    faixas_etarias = [{'quantidade': random.randint(1, 20), 'faixa_etaria': i.uuid} for i in faixas_etarias]

    data = {
        'alunos_com_dieta_especial_participantes': alunos_com_dieta,
        'escola': escola.uuid,
        'local': local,
        'solicitacao_kit_lanche': {
            'descricao': 'Um texto aleatório',
            'data': data,
            'kits': kits_escolhidos,
            'tempo_passeio': tempo_passeio
        },
        'faixas_etarias': faixas_etarias
    }

    serializer_obj = SolicitacaoKitLancheCEIAvulsaCreationSerializer(context={'request': FakeObject}, data=data)
    assert serializer_obj.is_valid()
