from rest_framework import serializers, status

from ...eol_servico.utils import EOLException
from ...terceirizada.models import Terceirizada
from ..models import Usuario


def senha_deve_ser_igual_confirmar_senha(senha: str, confirmar_senha: str):
    if senha != confirmar_senha:
        raise serializers.ValidationError('Senha e confirmar senha divergem')
    return True


def registro_funcional_e_cpf_sao_da_mesma_pessoa(usuario: Usuario, registro_funcional: str, cpf: str):
    if usuario.cpf != cpf or usuario.registro_funcional != registro_funcional:
        raise serializers.ValidationError('Erro ao cadastrar usuário')
    return True


def terceirizada_tem_esse_cnpj(terceirizada: Terceirizada, cnpj: str):
    if terceirizada.cnpj != cnpj:
        raise serializers.ValidationError('CNPJ da Empresa inválido')
    return True


def usuario_e_das_terceirizadas(usuario: Usuario):
    if not isinstance(usuario.vinculo_atual.instituicao, Terceirizada):
        raise serializers.ValidationError('Usuario já existe e não é Perfil Terceirizadas')
    return True


def deve_ter_mesmo_cpf(cpf_request: str, cpf_instance: str):
    if cpf_request != cpf_instance:
        raise serializers.ValidationError('CPF incorreto')
    return True


def usuario_pode_efetuar_cadastro(usuario: Usuario):
    try:
        if not usuario.pode_efetuar_cadastro:
            raise serializers.ValidationError('Erro ao cadastrar usuário')
    except EOLException as e:
        raise serializers.ValidationError(f'{e}')
    return True


def deve_ser_email_sme(email):
    if '@sme.prefeitura.sp.gov.br' not in email:
        raise serializers.ValidationError('Deve ser email da SME')
    return True


def usuario_e_vinculado_a_aquela_instituicao(descricao_instituicao: str, instituicoes_eol: list):
    mesma_instituicao = False
    for instituicao_eol in instituicoes_eol:
        if instituicao_eol['divisao'] in descricao_instituicao:
            mesma_instituicao = True
    if not mesma_instituicao:
        raise serializers.ValidationError('Instituições devem ser a mesma')
    return True


def usuario_nao_possui_vinculo_valido(usuario: Usuario):
    if usuario.vinculo_atual is not None:
        raise serializers.ValidationError('Usuário já possui vínculo válido', code=status.HTTP_400_BAD_REQUEST)
    return True
