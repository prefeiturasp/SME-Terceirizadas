import factory
from factory import DjangoModelFactory, Sequence, SubFactory
from faker import Faker

from sme_terceirizadas.escola.fixtures.factories.escola_factory import (
    EscolaFactory,
    FaixaEtariaFactory,
    LoteFactory,
    PeriodoEscolarFactory,
)
from sme_terceirizadas.inclusao_alimentacao.models import (
    DiasMotivosInclusaoDeAlimentacaoCEI,
    InclusaoAlimentacaoDaCEI,
    QuantidadeDeAlunosPorFaixaEtariaDaInclusaoDeAlimentacaoDaCEI,
)
from sme_terceirizadas.perfil.fixtures.factories.perfil_base_factories import (
    UsuarioFactory,
)

fake = Faker("pt_BR")


class InclusaoAlimentacaoDaCEIFactory(DjangoModelFactory):
    criado_por = SubFactory(UsuarioFactory)
    escola = SubFactory(EscolaFactory)
    rastro_lote = SubFactory(LoteFactory)
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


class QuantidadeDeAlunosPorFaixaEtariaDaInclusaoDeAlimentacaoDaCEIFactory(
    DjangoModelFactory
):
    inclusao_alimentacao_da_cei = SubFactory(InclusaoAlimentacaoDaCEIFactory)
    faixa_etaria = SubFactory(FaixaEtariaFactory)
    quantidade_alunos = Sequence(lambda n: fake.unique.random_int(min=1, max=100))
    periodo = SubFactory(PeriodoEscolarFactory)

    class Meta:
        model = QuantidadeDeAlunosPorFaixaEtariaDaInclusaoDeAlimentacaoDaCEI


class DiasMotivosInclusaoDeAlimentacaoCEIFactory(DjangoModelFactory):
    inclusao_cei = SubFactory(InclusaoAlimentacaoDaCEIFactory)

    class Meta:
        model = DiasMotivosInclusaoDeAlimentacaoCEI
