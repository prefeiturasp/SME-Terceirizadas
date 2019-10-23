from rest_framework import serializers


def senha_deve_ser_igual_confirmar_senha(senha: str, confirmar_senha: str):
    if senha != confirmar_senha:
        raise serializers.ValidationError('Senha e confirmar senha divergem')
    return True
