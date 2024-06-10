from factory import DjangoModelFactory, Sequence
from faker import Faker

from sme_terceirizadas.perfil.models import Usuario

fake = Faker("pt_BR")


class UsuarioFactory(DjangoModelFactory):
    nome = Sequence(lambda n: f"nome - {fake.unique.name()}")

    class Meta:
        model = Usuario
