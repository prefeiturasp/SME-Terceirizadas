from sme_terceirizadas.escola.models import FaixaEtaria

print("Criando faixas etárias")
FaixaEtaria.objects.bulk_create([
    FaixaEtaria(inicio=0, fim=1),
    FaixaEtaria(inicio=1, fim=4),
    FaixaEtaria(inicio=4, fim=6),
    FaixaEtaria(inicio=6, fim=7),
    FaixaEtaria(inicio=7, fim=8),
    FaixaEtaria(inicio=8, fim=12),
    FaixaEtaria(inicio=12, fim=24),
    FaixaEtaria(inicio=24, fim=48),
    FaixaEtaria(inicio=48, fim=72)
])
