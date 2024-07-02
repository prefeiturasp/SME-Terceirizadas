from factory import DjangoModelFactory, Sequence, SubFactory
from faker import Faker

from sme_terceirizadas.dados_comuns.models import LogSolicitacoesUsuario
from sme_terceirizadas.perfil.fixtures.factories.perfil_base_factories import (
    UsuarioFactory,
)

fake = Faker("pt_BR")


class LogSolicitacoesUsuarioFactory(DjangoModelFactory):
    uuid_original = fake.uuid4()
    status_evento = Sequence(lambda n: fake.random.randint(1, 30))
    solicitacao_tipo = Sequence(lambda n: fake.random.randint(1, 10))
    usuario = SubFactory(UsuarioFactory)
    justificativa = Sequence(lambda n: f"justificativa - {fake.unique.name()}")
    resposta_sim_nao = fake.boolean()

    class Meta:
        model = LogSolicitacoesUsuario
