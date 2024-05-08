from factory import DjangoModelFactory, Sequence, SubFactory
from faker import Faker

from sme_terceirizadas.imr.models import (
    CategoriaOcorrencia,
    FaixaPontuacaoIMR,
    TipoGravidade,
    TipoOcorrencia,
    TipoPenalidade,
    UtensilioMesa,
    UtensilioCozinha,
    Equipamento
)
from sme_terceirizadas.terceirizada.fixtures.factories.terceirizada_factory import (
    EditalFactory,
)

fake = Faker("pt_BR")


class TipoGravidadeFactory(DjangoModelFactory):
    class Meta:
        model = TipoGravidade

    tipo = Sequence(lambda n: f"tipo - {fake.unique.name()}")


class TipoPenalidadeFactory(DjangoModelFactory):
    class Meta:
        model = TipoPenalidade

    edital = SubFactory(EditalFactory)
    numero_clausula = Sequence(lambda n: fake.unique.random_int(min=1, max=1000))
    descricao = Sequence(lambda n: f"descrição - {fake.unique.name()}")
    gravidade = SubFactory(TipoGravidadeFactory)


class CategoriaOcorrenciaFactory(DjangoModelFactory):
    class Meta:
        model = CategoriaOcorrencia

    nome = Sequence(lambda n: f"nome - {fake.unique.name()}")


class TipoOcorrenciaFactory(DjangoModelFactory):
    class Meta:
        model = TipoOcorrencia

    edital = SubFactory(EditalFactory)
    titulo = Sequence(lambda n: f"titulo - {fake.unique.name()}")
    descricao = Sequence(lambda n: f"descrição - {fake.unique.name()}")
    categoria = SubFactory(CategoriaOcorrenciaFactory)
    penalidade = SubFactory(TipoPenalidadeFactory)


class FaixaPontuacaoFactory(DjangoModelFactory):
    class Meta:
        model = FaixaPontuacaoIMR

    pontuacao_minima = Sequence(lambda n: fake.unique.random_int(min=1, max=100))
    pontuacao_maxima = Sequence(lambda n: fake.unique.random_int(min=1, max=100))
    porcentagem_desconto = Sequence(lambda n: fake.unique.random_int(min=1, max=100))


class UtensilioMesaFactory(DjangoModelFactory):

    class Meta:
        model = UtensilioMesa

    nome = Sequence(lambda n: f"nome - {fake.unique.name()}")


class UtensilioCozinhaFactory(DjangoModelFactory):

    class Meta:
        model = UtensilioCozinha

    nome = Sequence(lambda n: f"nome - {fake.unique.name()}")


class EquipamentoFactory(DjangoModelFactory):

    class Meta:
        model = Equipamento

    nome = Sequence(lambda n: f"nome - {fake.unique.name()}")
