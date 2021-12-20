import pytest
from pydantic import ValidationError

from ..schemas import ArquivoCargaAlimentosSchema, ArquivoCargaDietaEspecialSchema, ArquivoCargaUsuariosDiretorSchema


def test_schema_arquivo_alimento_e_substitutos():
    dicionario_dados = {'nome': 'ARROZ'}
    assert ArquivoCargaAlimentosSchema(**dicionario_dados)


def test_schema_arquivo_alimento_e_substitutos_value_error():
    dicionario_dados = {'nome': None}
    with pytest.raises(ValidationError):
        ArquivoCargaAlimentosSchema(**dicionario_dados)


def test_schema_arquivo_importa_dieta_especial():
    dicionario_dados = {
        'dre': 'BT',
        'tipo_gestao': 'Terceirizada',
        'tipo_unidade': 'DIRETA',
        'codigo_escola': '12345678',
        'nome_unidade': 'Uma Unidade',
        'codigo_eol_aluno': '1234567',
        'nome_aluno': 'Anderson Marques',
        'data_nascimento': '11/01/1989',
        'data_ocorrencia': '11/01/1989',
        'codigo_diagnostico': 'Aluno Alérgico',
        'protocolo_dieta': 'Alérgico',
        'codigo_categoria_dieta': 'A'
    }
    assert ArquivoCargaDietaEspecialSchema(**dicionario_dados)


def test_schema_arquivo_importa_dieta_especial_erro_codigo_eol_aluno():
    dicionario_dados = {
        'dre': 'BT',
        'tipo_gestao': 'Terceirizada',
        'tipo_unidade': 'DIRETA',
        'codigo_escola': '12345678',
        'nome_unidade': 'Uma Unidade',
        'codigo_eol_aluno': '123456',
        'nome_aluno': 'Anderson Marques',
        'data_nascimento': '11/01/1989',
        'data_ocorrencia': '11/01/1989',
        'codigo_diagnostico': 'Aluno Alérgico',
        'protocolo_dieta': 'Alérgico',
        'codigo_categoria_dieta': 'A'
    }
    with pytest.raises(ValueError):
        ArquivoCargaDietaEspecialSchema(**dicionario_dados)


def test_schema_arquivo_importa_usuario_diretor():
    dicionario_dados = {
        'dre': 'FB',
        'unidade_escola': 'EMEF SEBASTIAO NOGUEIRA DE LIMA, DES',
        'codigo_eol_escola': 94251,
        'nome_diretor': 'Marcio Roberto Thomaz',
        'rg_diretor': '21.304.995-8',
        'rf_diretor': 7253419,
        'cpf_diretor': '256.254.608-33',
        'email_diretor': 'marcio.thomaz@sme.prefeitura.sp.gov.br',
        'telefone_diretor': 991579658,
        'nome_assistente': 'Rosangela Loffreda de Almeida',
        'rg_assistente': '4.920.448-6',
        'rf_assistente': '835845.1',
        'cpf_assistente': '054.941.358-88',
        'email_assistente': 'rosangela.almeida@sme.prefeitura.sp.gov.br',
        'telefone_assistente': 997490773
    }

    assert ArquivoCargaUsuariosDiretorSchema(**dicionario_dados)


def test_schema_arquivo_importa_usuario_diretor_cpf_erro():
    dicionario_dados = {
        'dre': 'FB',
        'unidade_escola': 'EMEF SEBASTIAO NOGUEIRA DE LIMA, DES',
        'codigo_eol_escola': 94251,
        'nome_diretor': 'Marcio Roberto Thomaz',
        'rg_diretor': '21.304.995-8',
        'rf_diretor': 7253419,
        'cpf_diretor': '256.254.608-339',
        'email_diretor': 'marcio.thomaz@sme.prefeitura.sp.gov.br',
        'telefone_diretor': 991579658,
        'nome_assistente': 'Rosangela Loffreda de Almeida',
        'rg_assistente': '4.920.448-6',
        'rf_assistente': '835845.1',
        'cpf_assistente': '054.941.358-88',
        'email_assistente': 'rosangela.almeida@sme.prefeitura.sp.gov.br',
        'telefone_assistente': 997490773
    }
    with pytest.raises(ValueError):
        ArquivoCargaUsuariosDiretorSchema(**dicionario_dados)


def test_schema_arquivo_importa_usuario_diretor_cpf_vazio_erro():
    dicionario_dados = {
        'dre': 'FB',
        'unidade_escola': 'EMEF SEBASTIAO NOGUEIRA DE LIMA, DES',
        'codigo_eol_escola': 94251,
        'nome_diretor': 'Marcio Roberto Thomaz',
        'rg_diretor': '21.304.995-8',
        'rf_diretor': 7253419,
        'cpf_diretor': '',
        'email_diretor': 'marcio.thomaz@sme.prefeitura.sp.gov.br',
        'telefone_diretor': 991579658,
        'nome_assistente': 'Rosangela Loffreda de Almeida',
        'rg_assistente': '4.920.448-6',
        'rf_assistente': '835845.1',
        'cpf_assistente': '054.941.358-88',
        'email_assistente': 'rosangela.almeida@sme.prefeitura.sp.gov.br',
        'telefone_assistente': 997490773
    }
    with pytest.raises(ValidationError):
        ArquivoCargaUsuariosDiretorSchema(**dicionario_dados)


def test_schema_arquivo_importa_usuario_diretor_rf_com_erro():
    dicionario_dados = {
        'dre': 'FB',
        'unidade_escola': 'EMEF SEBASTIAO NOGUEIRA DE LIMA, DES',
        'codigo_eol_escola': '94251',
        'nome_diretor': 'Marcio Roberto Thomaz',
        'rg_diretor': '21.304.995-8',
        'rf_diretor': '72534',
        'cpf_diretor': '256.254.608-33',
        'email_diretor': 'marcio.thomaz@sme.prefeitura.sp.gov.br',
        'telefone_diretor': 991579658,
        'nome_assistente': 'Rosangela Loffreda de Almeida',
        'rg_assistente': '4.920.448-6',
        'rf_assistente': '835845.1',
        'cpf_assistente': '054.941.358-88',
        'email_assistente': 'rosangela.almeida@sme.prefeitura.sp.gov.br',
        'telefone_assistente': 997490773
    }
    with pytest.raises(ValueError):
        ArquivoCargaUsuariosDiretorSchema(**dicionario_dados)


def test_schema_arquivo_importa_usuario_diretor_rf_vazio():
    dicionario_dados = {
        'dre': 'FB',
        'unidade_escola': 'EMEF SEBASTIAO NOGUEIRA DE LIMA, DES',
        'codigo_eol_escola': '94251',
        'nome_diretor': 'Marcio Roberto Thomaz',
        'rg_diretor': '21.304.995-8',
        'rf_diretor': '',
        'cpf_diretor': '256.254.608-33',
        'email_diretor': 'marcio.thomaz@sme.prefeitura.sp.gov.br',
        'telefone_diretor': 991579658,
        'nome_assistente': 'Rosangela Loffreda de Almeida',
        'rg_assistente': '4.920.448-6',
        'rf_assistente': '835845.1',
        'cpf_assistente': '054.941.358-88',
        'email_assistente': 'rosangela.almeida@sme.prefeitura.sp.gov.br',
        'telefone_assistente': 997490773
    }
    with pytest.raises(ValueError):
        ArquivoCargaUsuariosDiretorSchema(**dicionario_dados)


def test_schema_arquivo_importa_usuario_assistente_rf_com_erro():
    dicionario_dados = {
        'dre': 'FB',
        'unidade_escola': 'EMEF SEBASTIAO NOGUEIRA DE LIMA, DES',
        'codigo_eol_escola': 94251,
        'nome_diretor': 'Marcio Roberto Thomaz',
        'rg_diretor': '21.304.995-8',
        'rf_diretor': 7253419,
        'cpf_diretor': '256.254.608-33',
        'email_diretor': 'marcio.thomaz@sme.prefeitura.sp.gov.br',
        'telefone_diretor': 991579658,
        'nome_assistente': 'Rosangela Loffreda de Almeida',
        'rg_assistente': '4.920.448-6',
        'rf_assistente': '83584',
        'cpf_assistente': '054.941.358-88',
        'email_assistente': 'rosangela.almeida@sme.prefeitura.sp.gov.br',
        'telefone_assistente': 997490773
    }

    with pytest.raises(ValueError):
        ArquivoCargaUsuariosDiretorSchema(**dicionario_dados)


def test_schema_arquivo_importa_usuario_assistente_rf_vazio():
    dicionario_dados = {
        'dre': 'FB',
        'unidade_escola': 'EMEF SEBASTIAO NOGUEIRA DE LIMA, DES',
        'codigo_eol_escola': 94251,
        'nome_diretor': 'Marcio Roberto Thomaz',
        'rg_diretor': '21.304.995-8',
        'rf_diretor': 7253419,
        'cpf_diretor': '256.254.608-33',
        'email_diretor': 'marcio.thomaz@sme.prefeitura.sp.gov.br',
        'telefone_diretor': 991579658,
        'nome_assistente': 'Rosangela Loffreda de Almeida',
        'rg_assistente': '4.920.448-6',
        'rf_assistente': '',
        'cpf_assistente': '054.941.358-88',
        'email_assistente': 'rosangela.almeida@sme.prefeitura.sp.gov.br',
        'telefone_assistente': 997490773
    }

    with pytest.raises(ValidationError):
        ArquivoCargaUsuariosDiretorSchema(**dicionario_dados)
