from rest_framework import serializers


def contrato_pertence_a_empresa(contrato, empresa):
    if contrato not in empresa.contratos.all():
        raise serializers.ValidationError('Contrato deve pertencer a empresa selecionada')
    return True


def valida_parametros_calendario(mes, ano):
    if not (mes and ano):
        raise serializers.ValidationError('mes e ano são parametros obrigatórios')
    mes = int(mes)
    ano = int(ano)
    if not (1 <= mes <= 12):
        raise serializers.ValidationError('Informe um mês valido, deve ser um número entre 1 a 12')
    if len(str(ano)) != 4:
        raise serializers.ValidationError('Informe um ano valido')
