import json

from faker import Faker
from freezegun import freeze_time
from model_mommy import mommy
from rest_framework import status

from ..models import CategoriaPerguntaFrequente, Notificacao, PerguntaFrequente

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


def test_get_notificacao_quantidade_de_nao_lidos(usuario_teste_notificacao_autenticado, notificacao):
    user, client = usuario_teste_notificacao_autenticado
    response = client.get(
        f'/notificacoes/quantidade-nao-lidos/', content_type='application/json')
    result = json.loads(response.content)
    assert response.status_code == status.HTTP_200_OK
    assert result['quantidade_nao_lidos'] == 1


def test_get_notificacoes(usuario_teste_notificacao_autenticado, notificacao):
    user, client = usuario_teste_notificacao_autenticado
    response = client.get(
        f'/notificacoes/', content_type='application/json')
    result = json.loads(response.content)
    esperado = {
        'next': None,
        'previous': None,
        'count': 1,
        'page_size': 5,
        'results': [
            {
                'uuid': str(notificacao.uuid),
                'titulo': notificacao.titulo,
                'descricao': notificacao.descricao,
                'criado_em': notificacao.criado_em.strftime('%d/%m/%Y'),
                'hora': notificacao.hora.strftime('%H:%M'),
                'tipo': Notificacao.TIPO_NOTIFICACAO_NOMES[notificacao.tipo],
                'categoria': Notificacao.CATEGORIA_NOTIFICACAO_NOMES[notificacao.categoria],
                'link': notificacao.link,
                'lido': notificacao.lido,
                'resolvido': notificacao.resolvido,
            }
        ]
    }
    assert response.status_code == status.HTTP_200_OK
    assert result == esperado


def test_get_notificacoes_gerais(usuario_teste_notificacao_autenticado, notificacao):
    user, client = usuario_teste_notificacao_autenticado
    response = client.get(
        f'/notificacoes/gerais/', content_type='application/json')
    result = json.loads(response.content)
    esperado = {
        'next': None,
        'previous': None,
        'count': 1,
        'page_size': 5,
        'results': [
            {
                'uuid': str(notificacao.uuid),
                'titulo': notificacao.titulo,
                'descricao': notificacao.descricao,
                'criado_em': notificacao.criado_em.strftime('%d/%m/%Y'),
                'hora': notificacao.hora.strftime('%H:%M'),
                'tipo': Notificacao.TIPO_NOTIFICACAO_NOMES[notificacao.tipo],
                'categoria': Notificacao.CATEGORIA_NOTIFICACAO_NOMES[notificacao.categoria],
                'link': notificacao.link,
                'lido': notificacao.lido,
                'resolvido': notificacao.resolvido,
            }
        ]
    }
    assert response.status_code == status.HTTP_200_OK
    assert result == esperado


def test_get_pendencias_nao_resolvidas(usuario_teste_notificacao_autenticado, notificacao_de_pendencia):
    user, client = usuario_teste_notificacao_autenticado
    response = client.get(
        f'/notificacoes/pendencias-nao-resolvidas/', content_type='application/json')
    result = json.loads(response.content)
    esperado = {
        'next': None,
        'previous': None,
        'count': 1,
        'page_size': 5,
        'results': [
            {
                'uuid': str(notificacao_de_pendencia.uuid),
                'titulo': notificacao_de_pendencia.titulo,
                'descricao': notificacao_de_pendencia.descricao,
                'criado_em': notificacao_de_pendencia.criado_em.strftime('%d/%m/%Y'),
                'hora': notificacao_de_pendencia.hora.strftime('%H:%M'),
                'tipo': Notificacao.TIPO_NOTIFICACAO_NOMES[notificacao_de_pendencia.tipo],
                'categoria': Notificacao.CATEGORIA_NOTIFICACAO_NOMES[notificacao_de_pendencia.categoria],
                'link': notificacao_de_pendencia.link,
                'lido': notificacao_de_pendencia.lido,
                'resolvido': notificacao_de_pendencia.resolvido,
            }
        ]
    }
    assert response.status_code == status.HTTP_200_OK
    assert result == esperado


def test_put_notificacao_marcar_como_lida(usuario_teste_notificacao_autenticado, notificacao):
    user, client = usuario_teste_notificacao_autenticado
    payload = {
        'uuid': str(notificacao.uuid),
        'lido': True
    }

    response = client.put(
        f'/notificacoes/marcar-lido/', data=json.dumps(payload), content_type='application/json')
    assert response.status_code == status.HTTP_200_OK
