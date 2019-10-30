from rest_framework import serializers


def deve_ser_mesma_instituicao(instituicao_objeto: str, instituicao_eol: str):
    if instituicao_eol not in instituicao_objeto:
        raise serializers.ValidationError('Instituições devem ser a mesma')
    return True
