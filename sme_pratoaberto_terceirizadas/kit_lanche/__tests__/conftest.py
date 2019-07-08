import pytest
from faker import Faker
from model_mommy import mommy

from .. import models

fake = Faker('pt_BR')
fake.seed(420)


@pytest.fixture
def kit_lanche():
    itens = mommy.make(
        models.ItemKitLanche, nome='Barra de Cereal (20 a 25 g embalagem individual)', _quantity=3)
    return mommy.make(models.KitLanche, nome='kit lance nro tal',
                      itens=itens)
