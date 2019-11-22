from rest_framework import serializers, status

from ...perfil.models import Usuario


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
