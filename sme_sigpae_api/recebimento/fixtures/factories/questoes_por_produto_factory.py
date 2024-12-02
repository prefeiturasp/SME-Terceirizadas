from factory import DjangoModelFactory, SubFactory

from sme_sigpae_api.pre_recebimento.fixtures.factories.ficha_tecnica_do_produto_factory import (
    FichaTecnicaFactory,
)
from sme_sigpae_api.recebimento.models import QuestoesPorProduto


class QuestoesPorProdutoFactory(DjangoModelFactory):
    class Meta:
        model = QuestoesPorProduto

    ficha_tecnica = SubFactory(FichaTecnicaFactory)
