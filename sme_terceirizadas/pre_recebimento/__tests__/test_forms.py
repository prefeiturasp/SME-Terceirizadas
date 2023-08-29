import pytest

from sme_terceirizadas.pre_recebimento.forms import CaixaAltaNomeForm
from sme_terceirizadas.pre_recebimento.models.cronograma import UnidadeMedida

pytestmark = pytest.mark.django_db


def test_caixa_alta_nome_form_validation():
    class CaixaAltaNomeFormComModelo(CaixaAltaNomeForm):
        class Meta:
            model = UnidadeMedida
            fields = ['nome', 'abreviacao']

    form = CaixaAltaNomeFormComModelo(data={'nome': 'teste', 'abreviacao': 't'})
    assert form.is_valid()
    assert form.cleaned_data['nome'] == 'TESTE'
