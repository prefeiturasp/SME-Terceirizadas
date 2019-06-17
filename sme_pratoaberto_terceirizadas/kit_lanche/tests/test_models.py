import pytest

pytestmark = pytest.mark.django_db


def test_meal_kit_attrs(meal_kit):
    assert meal_kit.nome == 'kit lance nro tal'
    assert meal_kit.descricao == 'este kit lanche foi feito por fulano em...'
    assert meal_kit.__str__() == 'kit lance nro tal'
    assert meal_kit.refeicoes.count() == 4


def test_meal_kit_meta(meal_kit):
    assert meal_kit._meta.verbose_name_plural == "Kit Lanche"
    assert meal_kit._meta.verbose_name == "Kits Lanche"


def test_order_meal_kit(order_meal_kit):
    assert order_meal_kit.localizacao == 'rua dos bobos numero 9'
    assert order_meal_kit.tempo_passeio_formulario in ['Até 4 horas (1 kit)', '5 a 7 horas (2 kits)',
                                                       '8 horas ou mais (3 kits)']
    assert order_meal_kit.opcao_desejada == 'Modelo l, l, l, l, l'  # ?
