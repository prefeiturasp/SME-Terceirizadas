from factory import DjangoModelFactory, Sequence, SubFactory
from factory.fuzzy import FuzzyInteger
from faker import Faker

from sme_terceirizadas.escola.fixtures.factories.escola_factory import EscolaFactory
from sme_terceirizadas.imr.models import (
    CategoriaOcorrencia,
    Equipamento,
    FaixaPontuacaoIMR,
    Insumo,
    Mobiliario,
    ObrigacaoPenalidade,
    ParametrizacaoOcorrencia,
    PerfilDiretorSupervisao,
    PeriodoVisita,
    ReparoEAdaptacao,
    TipoGravidade,
    TipoOcorrencia,
    TipoPenalidade,
    TipoPerguntaParametrizacaoOcorrencia,
    TipoRespostaModelo,
    UtensilioCozinha,
    UtensilioMesa,
)
from sme_terceirizadas.medicao_inicial.models import SolicitacaoMedicaoInicial
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


class ObrigacaoPenalidadeFactory(DjangoModelFactory):
    class Meta:
        model = ObrigacaoPenalidade

    tipo_penalidade = SubFactory(TipoPenalidadeFactory)
    descricao = Sequence(lambda n: f"descrição - {fake.unique.name()}")


class TipoRespostaModeloFactory(DjangoModelFactory):
    class Meta:
        model = TipoRespostaModelo

    nome = Sequence(lambda n: f"nome - {fake.unique.name()}")


class TipoPerguntaParametrizacaoOcorrenciaFactory(DjangoModelFactory):
    class Meta:
        model = TipoPerguntaParametrizacaoOcorrencia

    nome = Sequence(lambda n: f"nome - {fake.unique.name()}")
    tipo_resposta = SubFactory(TipoRespostaModeloFactory)


class CategoriaOcorrenciaFactory(DjangoModelFactory):
    class Meta:
        model = CategoriaOcorrencia

    nome = Sequence(lambda n: f"nome - {fake.unique.name()}")
    perfis = Sequence(
        lambda n: [
            fake.random_element(
                [PerfilDiretorSupervisao.DIRETOR, PerfilDiretorSupervisao.SUPERVISAO]
            )
        ]
    )
    posicao = FuzzyInteger(1)


class TipoOcorrenciaFactory(DjangoModelFactory):
    class Meta:
        model = TipoOcorrencia

    edital = SubFactory(EditalFactory)
    titulo = Sequence(lambda n: f"titulo - {fake.unique.name()}")
    descricao = Sequence(lambda n: f"descrição - {fake.unique.name()}")
    categoria = SubFactory(CategoriaOcorrenciaFactory)
    penalidade = SubFactory(TipoPenalidadeFactory)
    perfis = Sequence(
        lambda n: [
            fake.random_element(
                [PerfilDiretorSupervisao.DIRETOR, PerfilDiretorSupervisao.SUPERVISAO]
            )
        ]
    )
    posicao = FuzzyInteger(1)


class ParametrizacaoOcorrenciaFactory(DjangoModelFactory):
    class Meta:
        model = ParametrizacaoOcorrencia

    titulo = Sequence(lambda n: f"nome - {fake.unique.name()}")
    tipo_ocorrencia = SubFactory(TipoOcorrenciaFactory)
    tipo_pergunta = SubFactory(TipoPerguntaParametrizacaoOcorrenciaFactory)


class PeriodoVisitaFactory(DjangoModelFactory):
    nome = Sequence(lambda n: f"nome - {fake.unique.name()}")

    class Meta:
        model = PeriodoVisita


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


class MobiliarioFactory(DjangoModelFactory):
    class Meta:
        model = Mobiliario

    nome = Sequence(lambda n: f"nome - {fake.unique.name()}")


class ReparoEAdaptacaoFactory(DjangoModelFactory):
    class Meta:
        model = ReparoEAdaptacao

    nome = Sequence(lambda n: f"nome - {fake.unique.name()}")


class InsumoFactory(DjangoModelFactory):
    class Meta:
        model = Insumo

    nome = Sequence(lambda n: f"nome - {fake.unique.name()}")


class MedicaoInicialFactory(DjangoModelFactory):
    escola = SubFactory(EscolaFactory)

    class Meta:
        model = SolicitacaoMedicaoInicial
