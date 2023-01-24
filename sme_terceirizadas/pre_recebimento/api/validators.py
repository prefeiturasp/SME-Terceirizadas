from rest_framework import serializers


def contrato_pertence_a_empresa(contrato, empresa):
    if contrato not in empresa.contratos.all():
        raise serializers.ValidationError('Contrato deve pertencer a empresa selecionada')
    return True
