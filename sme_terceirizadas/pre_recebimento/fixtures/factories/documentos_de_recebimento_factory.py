from datetime import date, timedelta

from factory import DjangoModelFactory, LazyFunction, SubFactory
from faker import Faker

from sme_terceirizadas.pre_recebimento.fixtures.factories.cronograma_factory import (
    CronogramaFactory,
)
from sme_terceirizadas.pre_recebimento.models import (
    DataDeFabricaoEPrazo,
    DocumentoDeRecebimento,
    TipoDeDocumentoDeRecebimento,
)

fake = Faker("pt_BR")


class DocumentoDeRecebimentoFactory(DjangoModelFactory):
    class Meta:
        model = DocumentoDeRecebimento

    cronograma = SubFactory(CronogramaFactory)
    numero_laudo = fake.unique.random_int(min=10**9, max=(10**10) - 1)
    numero_lote_laudo = LazyFunction(
        lambda: ", ".join(
            [
                str(fake.random.randint(10000, 99999))
                for i in range(fake.random.randint(1, 10))
            ]
        )
    )


class TipoDeDocumentoDeRecebimentoFactory(DjangoModelFactory):
    class Meta:
        model = TipoDeDocumentoDeRecebimento

    documento_recebimento = SubFactory(DocumentoDeRecebimentoFactory)
    tipo_documento = TipoDeDocumentoDeRecebimento.TIPO_DOC_LAUDO


class DataDeFabricaoEPrazoFactory(DjangoModelFactory):
    class Meta:
        model = DataDeFabricaoEPrazo

    documento_recebimento = SubFactory(DocumentoDeRecebimentoFactory)
    data_fabricacao = LazyFunction(
        lambda: fake.date_time_between(
            start_date=date.today() - timedelta(days=fake.random.randint(1, 90))
        ).date()
    )
    data_validade = LazyFunction(
        lambda: fake.date_time_between(
            start_date=date.today() + timedelta(days=fake.random.randint(1, 90))
        ).date()
    )
