from rest_framework.serializers import ValidationError


def deve_ter_extensao_valida(nome: str):
    if nome.split('.')[len(nome.split('.')) - 1] not in ['doc', 'docx', 'pdf', 'png', 'jpg', 'jpeg']:
        raise ValidationError('Extensão inválida')
    return nome
