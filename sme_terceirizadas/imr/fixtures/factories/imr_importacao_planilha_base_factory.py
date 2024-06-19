import factory
from factory import DjangoModelFactory
from faker import Faker

from sme_terceirizadas.imr.models import (
    ImportacaoPlanilhaTipoOcorrencia,
    ImportacaoPlanilhaTipoPenalidade,
)

fake = Faker("pt_BR")


class ImportacaoPlanilhaTipoPenalidadeFactory(DjangoModelFactory):
    conteudo = factory.django.FileField()

    class Meta:
        model = ImportacaoPlanilhaTipoPenalidade


class ImportacaoPlanilhaTipoOcorrenciaFactory(DjangoModelFactory):
    conteudo = factory.django.FileField()

    class Meta:
        model = ImportacaoPlanilhaTipoOcorrencia
