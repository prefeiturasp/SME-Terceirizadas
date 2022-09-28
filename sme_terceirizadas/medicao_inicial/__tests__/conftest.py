import datetime

import pytest
from model_mommy import mommy


@pytest.fixture
def tipo_unidade_escolar():
    return mommy.make('TipoUnidadeEscolar', iniciais='EMEF')


@pytest.fixture
def dia_sobremesa_doce(tipo_unidade_escolar):
    return mommy.make('DiaSobremesaDoce', data=datetime.date(2022, 8, 8), tipo_unidade=tipo_unidade_escolar)


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
    emef = mommy.make('TipoUnidadeEscolar', iniciais='EMEF', uuid='1cc3253b-e297-42b3-8e57-ebfd115a1aba')
    mommy.make('Escola', tipo_unidade=emef, uuid='95ad02fb-d746-4e0c-95f4-0181a99bc192')
    mommy.make('TipoUnidadeEscolar', iniciais='CEU GESTAO', uuid='40ee89a7-dc70-4abb-ae21-369c67f2b9e3')
    mommy.make('TipoUnidadeEscolar', iniciais='CIEJA', uuid='ac4858ff-1c11-41f3-b539-7a02696d6d1b')
    return client
