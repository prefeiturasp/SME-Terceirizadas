from factory import DjangoModelFactory, Sequence
from faker import Faker

from sme_terceirizadas.recebimento.models import QuestaoConferencia

fake = Faker("pt_BR")


class QuestaoConferenciaFactory(DjangoModelFactory):
    class Meta:
        model = QuestaoConferencia

    questao = Sequence(lambda n: f"Questao {fake.unique.name()}")
    posicao = Sequence(lambda n: fake.unique.random_int(min=1, max=1000))
