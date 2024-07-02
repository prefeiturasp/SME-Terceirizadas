from factory import DjangoModelFactory, LazyAttribute, Sequence, SubFactory
from faker import Faker

from sme_terceirizadas.escola.constants import CEI_OU_EMEI, INFANTIL_OU_FUNDAMENTAL
from sme_terceirizadas.escola.models import (
    DiretoriaRegional,
    Escola,
    LogAlunosMatriculadosPeriodoEscola,
    Lote,
    PeriodoEscolar,
    TipoTurma,
    TipoUnidadeEscolar,
)
from sme_terceirizadas.terceirizada.fixtures.factories.terceirizada_factory import (
    EmpresaFactory,
)

fake = Faker("pt_BR")


class TipoUnidadeEscolarFactory(DjangoModelFactory):
    class Meta:
        model = TipoUnidadeEscolar


class DiretoriaRegionalFactory(DjangoModelFactory):
    class Meta:
        model = DiretoriaRegional

    nome = Sequence(lambda n: f"Diretoria regional {n} - {fake.unique.company()}")
    codigo_eol = Sequence(lambda n: fake.unique.random_int(min=1, max=999999))


class LoteFactory(DjangoModelFactory):
    nome = Sequence(lambda n: f"Lote {n} - {fake.unique.company()}")
    diretoria_regional = SubFactory(DiretoriaRegionalFactory)
    terceirizada = SubFactory(EmpresaFactory)

    class Meta:
        model = Lote


class EscolaFactory(DjangoModelFactory):
    class Meta:
        model = Escola

    nome = Sequence(lambda n: f"Escola {n} - {fake.unique.company()}")
    codigo_eol = Sequence(lambda n: fake.unique.random_int(min=1, max=999999))
    lote = SubFactory(LoteFactory)
    diretoria_regional = SubFactory(DiretoriaRegionalFactory)
    tipo_unidade = SubFactory(TipoUnidadeEscolarFactory)


class PeriodoEscolarFactory(DjangoModelFactory):
    class Meta:
        model = PeriodoEscolar

    nome = Sequence(lambda n: f"Periodo {n} - {fake.unique.word()}")


class LogAlunosMatriculadosPeriodoEscolaFactory(DjangoModelFactory):
    class Meta:
        model = LogAlunosMatriculadosPeriodoEscola

    escola = SubFactory(EscolaFactory)
    periodo_escolar = SubFactory(PeriodoEscolarFactory)
    quantidade_alunos = Sequence(lambda n: fake.unique.random_int(min=0, max=100))
    tipo_turma = Sequence(
        lambda n: [fake.random_element([choice[0] for choice in TipoTurma.choices()])]
    )
    cei_ou_emei = LazyAttribute(
        lambda o: fake.random_element(elements=[choice[0] for choice in CEI_OU_EMEI])
    )
    infantil_ou_fundamental = LazyAttribute(
        lambda o: fake.random_element(
            elements=[choice[0] for choice in INFANTIL_OU_FUNDAMENTAL]
        )
    )
