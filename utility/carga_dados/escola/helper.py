from unicodedata import normalize


def normaliza_nome(nome):
    nome = nome.replace(' / ', '/')
    nome = normalize('NFKD', nome).encode('ASCII', 'ignore').decode('ASCII')
    return nome


def somente_digitos(palavra):
    return ''.join(p for p in palavra if p in '0123456789')


def coloca_zero_a_esquerda(palavra, tam=6):
    tam_palavra = len(palavra)
    qtd_zeros = tam - tam_palavra
    zeros = '0' * qtd_zeros
    final = ''
    if tam_palavra < tam:
        final = zeros + palavra
    return final or palavra
