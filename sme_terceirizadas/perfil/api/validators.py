from rest_framework import serializers

from ..models import Usuario


def senha_deve_ser_igual_confirmar_senha(senha: str, confirmar_senha: str):
    if senha != confirmar_senha:
        raise serializers.ValidationError('Senha e confirmar senha divergem')
    return True


def registro_funcional_e_cpf_sao_da_mesma_pessoa(usuario: Usuario, registro_funcional: str, cpf: str):
    if usuario.cpf != cpf or usuario.registro_funcional != registro_funcional:
        raise serializers.ValidationError('Erro ao cadastrar usuário')
    return True


def usuario_pode_efetuar_cadastro(usuario: Usuario):
    if not usuario.pode_efetuar_cadastro:
        raise serializers.ValidationError('Erro ao cadastrar usuário')
    return True


def deve_ser_email_sme(email):
    if '@sme.prefeitura.sp.gov.br' not in email:
        raise serializers.ValidationError('Deve ser email da SME')
    return True
