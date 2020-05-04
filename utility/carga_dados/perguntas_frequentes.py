import random

from faker import Faker

from sme_terceirizadas.dados_comuns.models import CategoriaPerguntaFrequente, PerguntaFrequente

f = Faker('pt-br')
f.seed(420)

for i in range(random.randint(3, 7)):
    cat = CategoriaPerguntaFrequente.objects.create(nome=f.name())
    for j in range(random.randint(5, 10)):
        PerguntaFrequente.objects.create(
            categoria=cat,
            pergunta=f.text()[:100],
            resposta=f.text()
        )
