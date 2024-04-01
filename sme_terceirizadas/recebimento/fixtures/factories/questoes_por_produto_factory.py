from factory import DjangoModelFactory, SubFactory

from sme_terceirizadas.pre_recebimento.fixtures.factories.ficha_tecnica_do_produto_factory import (
    FichaTecnicaFactory,
)
from sme_terceirizadas.recebimento.models import QuestoesPorProduto


class QuestoesPorProdutoFactory(DjangoModelFactory):
    class Meta:
        model = QuestoesPorProduto

    ficha_tecnica = SubFactory(FichaTecnicaFactory)
