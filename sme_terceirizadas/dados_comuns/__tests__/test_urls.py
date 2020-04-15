from faker import Faker
from model_mommy import mommy

from ..models import PerguntaFrequente

fake = Faker('pt_BR')
fake.seed(420)


def test_url_cria_faq(client_autenticado_coordenador_codae):
    payload = {
        'pergunta': fake.text(),
        'resposta': fake.text()
    }

    client_autenticado_coordenador_codae.post(
        '/perguntas-frequentes/',
        content_type='application/json',
        data=payload
    )

    pergunta = PerguntaFrequente.objects.first()

    assert pergunta.pergunta == payload['pergunta']
    assert pergunta.resposta == payload['resposta']


def test_url_atualiza_faq(client_autenticado_coordenador_codae):
    pergunta = mommy.make(PerguntaFrequente)
    payload = {
        'pergunta': fake.text(),
        'resposta': fake.text()
    }

    client_autenticado_coordenador_codae.patch(
        f'/perguntas-frequentes/{pergunta.uuid}/',
        content_type='application/json',
        data=payload
    )

    pergunta = PerguntaFrequente.objects.first()

    assert pergunta.pergunta == payload['pergunta']
    assert pergunta.resposta == payload['resposta']
