import datetime
import json

import pytest
from faker import Faker
from model_mommy import mommy

from ...eol_servico.utils import EOLService
from ...escola.api.serializers import EscolaSimplissimaSerializer, VinculoInstituicaoSerializer
from ...perfil.models import Vinculo
from .. import models

fake = Faker('pt_BR')
fake.seed(420)


@pytest.fixture
def tipo_unidade_escolar():
    cardapio1 = mommy.make('cardapio.Cardapio', data=datetime.date(2019, 10, 11))
    cardapio2 = mommy.make('cardapio.Cardapio', data=datetime.date(2019, 10, 15))
    return mommy.make(models.TipoUnidadeEscolar,
                      iniciais=fake.name()[:10],
                      cardapios=[cardapio1, cardapio2])


@pytest.fixture
def tipo_gestao():
    return mommy.make(models.TipoGestao,
                      nome=fake.name())


@pytest.fixture
def diretoria_regional(escola):
    return mommy.make(models.DiretoriaRegional,
                      escolas=[escola],
                      nome=fake.name(),
                      make_m2m=True)


@pytest.fixture
def lote():
    return mommy.make(models.Lote, nome='lote', iniciais='lt')


@pytest.fixture
def escola(lote):
    return mommy.make(models.Escola,
                      nome=fake.name(),
                      codigo_eol=fake.name()[:6],
                      lote=lote)


@pytest.fixture
def escola_simplissima_serializer(escola):
    return EscolaSimplissimaSerializer(escola)


@pytest.fixture
def faixa_idade_escolar():
    return mommy.make(models.FaixaIdadeEscolar,
                      nome=fake.name())


@pytest.fixture
def codae(escola):
    return mommy.make(models.Codae,
                      make_m2m=True)


@pytest.fixture
def periodo_escolar():
    return mommy.make(models.PeriodoEscolar, nome='INTEGRAL')


@pytest.fixture
def escola_periodo_escolar(periodo_escolar):
    return mommy.make(models.EscolaPeriodoEscolar, periodo_escolar=periodo_escolar)


@pytest.fixture
def sub_prefeitura():
    return mommy.make(models.Subprefeitura)


@pytest.fixture
def vinculo(escola):
    return mommy.make(Vinculo, uuid='a19baa09-f8cc-49a7-a38d-2a38270ddf45', instituicao=escola)


@pytest.fixture
def vinculo_instituto_serializer(vinculo):
    return VinculoInstituicaoSerializer(vinculo)


@pytest.fixture
def aluno(escola):
    return mommy.make(models.Aluno,
                      nome='Fulano da Silva',
                      codigo_eol='000001',
                      data_nascimento=datetime.date(2000, 1, 1),
                      escola=escola)


@pytest.fixture
def client_autenticado_coordenador_codae(client, django_user_model):
    email, password, rf, cpf = ('cogestor_1@sme.prefeitura.sp.gov.br', 'adminadmin', '0000001', '44426575052')
    user = django_user_model.objects.create_user(password=password, email=email, registro_funcional=rf, cpf=cpf)
    client.login(email=email, password=password)

    codae = mommy.make('Codae', nome='CODAE', uuid='b00b2cf4-286d-45ba-a18b-9ffe4e8d8dfd')

    perfil_coordenador = mommy.make('Perfil', nome='COORDENADOR_GESTAO_ALIMENTACAO_TERCEIRIZADA', ativo=True,
                                    uuid='41c20c8b-7e57-41ed-9433-ccb92e8afaf1')
    mommy.make('Lote', uuid='143c2550-8bf0-46b4-b001-27965cfcd107')
    hoje = datetime.date.today()
    mommy.make('Vinculo', usuario=user, instituicao=codae, perfil=perfil_coordenador,
               data_inicial=hoje, ativo=True)

    return client


@pytest.fixture
def faixas_etarias_ativas():
    faixas = [
        (0, 1),
        (1, 4),
        (4, 6),
        (6, 8),
        (8, 12),
        (12, 24),
        (24, 48),
        (48, 72),
    ]
    return [mommy.make('FaixaEtaria', inicio=inicio, fim=fim, ativo=True) for (inicio, fim) in faixas]


@pytest.fixture
def faixas_etarias(faixas_etarias_ativas):
    return faixas_etarias_ativas + mommy.make('FaixaEtaria', ativo=False, _quantity=8)


# Data referencia = 2019-06-20
@pytest.fixture(params=[
    # (data, faixa, data_pertence_a_faixa) E800 noqa
    (datetime.date(2019, 6, 15), 0, 1, True),
    (datetime.date(2019, 6, 20), 0, 1, False),
    (datetime.date(2019, 5, 20), 0, 1, True),
    (datetime.date(2019, 5, 19), 0, 1, False),
    (datetime.date(2019, 4, 20), 0, 1, False),
    (datetime.date(2019, 4, 20), 1, 3, True),
    (datetime.date(2019, 2, 10), 1, 3, False),
])
def datas_e_faixas(request):
    (data, inicio_faixa, fim_faixa, eh_pertencente) = request.param
    return (data, mommy.make('FaixaEtaria', inicio=inicio_faixa, fim=fim_faixa, ativo=True), eh_pertencente)


@pytest.fixture
def eolservice_get_informacoes_escola_turma_aluno(monkeypatch):
    with open('sme_terceirizadas/escola/__tests__/massa_eolservice_get_informacoes_escola_turma_aluno.json') as jsfile:
        js = json.load(jsfile)
    return monkeypatch.setattr(
        EOLService,
        'get_informacoes_escola_turma_aluno',
        lambda x: js['results']
    )
