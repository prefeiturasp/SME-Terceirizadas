import pytest
from model_mommy import mommy

from sme_terceirizadas.dieta_especial.models import (
    AlergiaIntolerancia,
    ArquivoCargaAlimentosSubstitutos,
    ArquivoCargaDietaEspecial,
    ArquivoCargaUsuariosEscola,
    ClassificacaoDieta,
    SolicitacaoDietaEspecial
)


@pytest.fixture
def arquivo_carga_dieta_especial():
    return mommy.make(ArquivoCargaDietaEspecial)


@pytest.fixture
def arquivo_carga_alimentos_e_substitutos():
    return mommy.make(ArquivoCargaAlimentosSubstitutos)


@pytest.fixture
def arquivo_carga_usuarios_escola():
    return mommy.make(ArquivoCargaUsuariosEscola)


@pytest.fixture
def dieta_especial_ativa():
    aluno = mommy.make('escola.Aluno', codigo_eol='1234567', nome='TESTE ALUNO DIETA')
    escola = mommy.make('escola.Escola', codigo_codae='12345678')
    classificacao = mommy.make(ClassificacaoDieta, nome='Tipo A')
    alergias_set = mommy.prepare(AlergiaIntolerancia, descricao='Aluno Alérgico', _quantity=1)
    solicitacao = mommy.make(
        SolicitacaoDietaEspecial,
        aluno=aluno,
        ativo=True,
        classificacao=classificacao,
        escola_destino=escola,
        nome_protocolo='Alérgico',
        alergias_intolerancias=alergias_set,
        eh_importado=True
    )
    return solicitacao


@pytest.fixture
def usuario():
    return mommy.make('perfil.Usuario')
