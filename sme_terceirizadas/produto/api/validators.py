from rest_framework import serializers


def deve_ter_extensao_valida(nome: str):
    if nome.split('.')[len(nome.split('.')) - 1] not in ['doc', 'docx', 'pdf', 'png', 'jpg', 'jpeg']:
        raise serializers.ValidationError('Extensão inválida')
    return nome
