import pytest
from model_mommy import mommy

from sme_terceirizadas.terceirizada.models import Edital

pytestmark = pytest.mark.django_db


def test_manager_edital_check_name_alrady_in_edital_ok():
    edital_1 = mommy.make('terceirizada.Edital', numero='Edital Numero 1')
    edital_2 = mommy.make('terceirizada.Edital', numero='Edital Numero 2')
    editais = [edital_1.uuid, edital_2.uuid]
    mommy.make('dieta_especial.ProtocoloPadraoDietaEspecial', nome_protocolo='ALERGIA - ABACATE', editais=[edital_1])
    assert 'Edital Numero 1' in Edital.objects.check_editais_already_has_nome_protocolo(
        editais, 'ALERGIA - ABACATE')[0]['numero']
