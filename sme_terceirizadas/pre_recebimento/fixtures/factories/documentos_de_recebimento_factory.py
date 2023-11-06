from factory import DjangoModelFactory, SubFactory
from faker import Faker

from sme_terceirizadas.pre_recebimento.fixtures.factories.cronograma_factory import CronogramaFactory
from sme_terceirizadas.pre_recebimento.models import DocumentoDeRecebimento, TipoDeDocumentoDeRecebimento

fake = Faker('pt_BR')


class DocumentoDeRecebimentoFactory(DjangoModelFactory):
    class Meta:
        model = DocumentoDeRecebimento

    cronograma = SubFactory(CronogramaFactory)
    numero_laudo = fake.unique.random_int(min=10 ** 9, max=(10 ** 10) - 1)


class TipoDeDocumentoDeRecebimentoFactory(DjangoModelFactory):
    class Meta:
        model = TipoDeDocumentoDeRecebimento

    documento_recebimento = SubFactory(DocumentoDeRecebimentoFactory)
    tipo_documento = TipoDeDocumentoDeRecebimento.TIPO_DOC_LAUDO
