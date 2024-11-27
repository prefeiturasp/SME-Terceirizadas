import factory
from factory import DjangoModelFactory, SubFactory

from sme_terceirizadas.escola.fixtures.factories.escola_factory import (
    EscolaFactory,
    PeriodoEscolarFactory,
)
from sme_terceirizadas.inclusao_alimentacao.models import InclusaoAlimentacaoDaCEI
from sme_terceirizadas.perfil.fixtures.factories.perfil_base_factories import (
    UsuarioFactory,
)


class InclusaoAlimentacaoDaCEIFactory(DjangoModelFactory):
    criado_por = SubFactory(UsuarioFactory)
    escola = SubFactory(EscolaFactory)
    periodo_escolar = SubFactory(PeriodoEscolarFactory)

    @factory.post_generation
    def tipos_alimentacao(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for tipo_alimentacao in extracted:
                self.tipos_alimentacao.add(tipo_alimentacao)

    class Meta:
        model = InclusaoAlimentacaoDaCEI
