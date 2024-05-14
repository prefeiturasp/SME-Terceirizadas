import pytest
import datetime
from model_mommy import mommy
from sme_terceirizadas.dados_comuns import constants
from sme_terceirizadas.imr.models import PerfilDiretorSupervisao


@pytest.fixture
def codae():
    return mommy.make("Codae")


@pytest.fixture
def client_autenticado_vinculo_coordenador_supervisao_nutricao(
    client, django_user_model, codae
):
    email = "test@test.com"
    password = constants.DJANGO_ADMIN_PASSWORD
    user = django_user_model.objects.create_user(
        username=email, password=password, email=email, registro_funcional="8888888"
    )
    perfil_supervisao_nutricao = mommy.make(
        "Perfil",
        nome=constants.COORDENADOR_SUPERVISAO_NUTRICAO,
        ativo=True,
        uuid="41c20c8b-7e57-41ed-9433-ccb92e8afaf1",
    )

    mommy.make(
        "Vinculo",
        usuario=user,
        instituicao=codae,
        perfil=perfil_supervisao_nutricao,
        data_inicial=datetime.date.today(),
        ativo=True,
    )
    client.login(username=email, password=password)
    return client


@pytest.fixture
def tipo_ocorrencia_nutrisupervisor_com_parametrizacao(
    edital_factory,
    categoria_ocorrencia_factory,
    tipo_ocorrencia_factory,
    parametrizacao_ocorrencia_factory,
    obrigacao_penalidade_factory
):
    edital = edital_factory.create(eh_imr=True)

    categoria = categoria_ocorrencia_factory.create(perfis=[PerfilDiretorSupervisao.SUPERVISAO])

    tipo_ocorrencia = tipo_ocorrencia_factory.create(
        edital=edital,
        descricao='Ocorrencia 1',
        perfis=[PerfilDiretorSupervisao.SUPERVISAO],
        categoria=categoria
    )

    obrigacao_penalidade_factory.create(
        tipo_penalidade=tipo_ocorrencia.penalidade
    )

    parametrizacao_ocorrencia_factory.create(
        tipo_ocorrencia=tipo_ocorrencia
    )

    return tipo_ocorrencia
