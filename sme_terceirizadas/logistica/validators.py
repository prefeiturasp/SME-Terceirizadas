from django.core import validators

apenas_letras_validation = validators.RegexValidator(
    regex=r'/[a-zA-Z]+/g', message='Digite apenas letras'
)

letras_e_numeros_validation = validators.RegexValidator(
    regex=r'/[^A-Za-z0-9]+/g', message='Digite apenas letras e números'
)
