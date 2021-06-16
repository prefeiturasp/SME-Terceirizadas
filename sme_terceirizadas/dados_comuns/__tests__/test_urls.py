from faker import Faker
from freezegun import freeze_time
from model_mommy import mommy

from ..models import CategoriaPerguntaFrequente, PerguntaFrequente

fake = Faker('pt_BR')
fake.seed(420)


def test_url_cria_faq(client_autenticado_coordenador_codae):
    categoria = mommy.make(CategoriaPerguntaFrequente)

    payload = {
        'pergunta': fake.text(),
        'resposta': fake.text(),
        'categoria': categoria.uuid
    }

    client_autenticado_coordenador_codae.post(
        '/perguntas-frequentes/',
        content_type='application/json',
        data=payload
    )

    pergunta = PerguntaFrequente.objects.first()

    assert pergunta.pergunta == payload['pergunta']
    assert pergunta.resposta == payload['resposta']
    assert categoria.uuid == payload['categoria']


def test_url_atualiza_faq(client_autenticado_coordenador_codae):
    pergunta = mommy.make(PerguntaFrequente)
    categoria = mommy.make(CategoriaPerguntaFrequente)
    payload = {
        'pergunta': fake.text(),
        'resposta': fake.text(),
        'categoria': categoria.uuid
    }

    client_autenticado_coordenador_codae.patch(
        f'/perguntas-frequentes/{pergunta.uuid}/',
        content_type='application/json',
        data=payload
    )

    pergunta = PerguntaFrequente.objects.first()

    assert pergunta.pergunta == payload['pergunta']
    assert pergunta.resposta == payload['resposta']
    assert categoria.uuid == payload['categoria']


@freeze_time('2021-06-16')
def test_proximo_dia_util_suspensao_alimentacao_segunda(client_autenticado):
    from sme_terceirizadas.dados_comuns.constants import obter_dias_uteis_apos_hoje
    result = obter_dias_uteis_apos_hoje(3)
    assert str(result) == '2021-06-21'


@freeze_time('2021-06-18')
def test_proximo_dia_util_suspensao_alimentacao_sexta(client_autenticado):
    from sme_terceirizadas.dados_comuns.constants import obter_dias_uteis_apos_hoje
    result = obter_dias_uteis_apos_hoje(3)
    assert str(result) == '2021-06-23'
