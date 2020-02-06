from rest_framework.serializers import ValidationError


def deve_ter_extensao_valida(nome: str):
    if nome.split('.')[len(nome.split('.')) - 1] not in ['doc', 'docx', 'pdf', 'png', 'jpg', 'jpeg']:
        raise ValidationError('Extensão inválida')
    return nome


def deve_ter_atributos(data, atributos):
    for atributo in atributos:
        if atributo not in data:
            raise ValidationError(f'deve ter atributo {atributo}')


def atributos_lista_nao_vazios(data, atributos):
    for atributo in atributos:
        if len(data[atributo]) < 1:
            raise ValidationError(f'atributo {atributo} não pode ser vazio')


def atributos_string_nao_vazios(data, atributos):
    for atributo in atributos:
        if data[atributo] == '':
            raise ValidationError(f'atributo {atributo} não pode ser vazio')
