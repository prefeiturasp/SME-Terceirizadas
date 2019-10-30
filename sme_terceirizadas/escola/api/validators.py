from rest_framework import serializers


def usuario_e_vinculado_a_aquela_instituicao(descricao_instituicao: str, instituicoes_eol: list):
    mesma_instituicao = False
    for instituicao_eol in instituicoes_eol:
        if instituicao_eol['divisao'] in descricao_instituicao:
            mesma_instituicao = True
    if not mesma_instituicao:
        raise serializers.ValidationError('Instituições devem ser a mesma')
    return True
