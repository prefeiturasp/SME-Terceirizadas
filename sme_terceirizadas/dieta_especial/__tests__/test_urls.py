from rest_framework import status

from ..constants import (
    ENDPOINT_ALERGIAS_INTOLERANCIAS,
    ENDPOINT_CLASSIFICACOES_DIETA,
    ENDPOINT_MOTIVOS_NEGACAO,
    ENDPOINT_TIPOS_DIETA_ESPECIAL
)
from ..models import (
    AlergiaIntolerancia,
    Anexo,
    ClassificacaoDieta,
    MotivoNegacao,
    SolicitacaoDietaEspecial,
    TipoDieta
)
from ...dados_comuns.fluxo_status import DietaEspecialWorkflow


def endpoint_lista(client_autenticado, endpoint, quantidade):
    response = client_autenticado.get(f'/{endpoint}/')
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert len(json) == quantidade


def test_url_endpoint_lista_alergias_intolerancias(client_autenticado,
                                                   alergias_intolerancias):
    endpoint_lista(
        client_autenticado,
        ENDPOINT_ALERGIAS_INTOLERANCIAS,
        quantidade=2
    )


def test_url_endpoint_lista_classificacoes_dieta(client_autenticado,
                                                 classificacoes_dieta):
    endpoint_lista(
        client_autenticado,
        ENDPOINT_CLASSIFICACOES_DIETA,
        quantidade=3
    )


def test_url_endpoint_lista_motivos_negacao(client_autenticado,
                                            motivos_negacao):
    endpoint_lista(
        client_autenticado,
        ENDPOINT_MOTIVOS_NEGACAO,
        quantidade=4
    )


def test_url_endpoint_lista_tipos_dieta(client_autenticado,
                                        tipos_dieta):
    endpoint_lista(
        client_autenticado,
        ENDPOINT_TIPOS_DIETA_ESPECIAL,
        quantidade=5
    )


def endpoint_detalhe(client_autenticado, endpoint, modelo, tem_nome=False):
    obj = modelo.objects.first()
    response = client_autenticado.get(f'/{endpoint}/{obj.id}/')
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert obj.descricao == json['descricao']
    if tem_nome:
        assert obj.nome == json['nome']


def test_url_endpoint_detalhe_alergias_intolerancias(client_autenticado,
                                                     alergias_intolerancias):
    endpoint_detalhe(
        client_autenticado,
        ENDPOINT_ALERGIAS_INTOLERANCIAS,
        AlergiaIntolerancia
    )


def test_url_endpoint_detalhe_classificacoes_dieta(client_autenticado,
                                                   classificacoes_dieta):
    endpoint_detalhe(
        client_autenticado,
        ENDPOINT_CLASSIFICACOES_DIETA,
        ClassificacaoDieta,
        tem_nome=True
    )


def test_url_endpoint_detalhe_motivos_negacao(client_autenticado,
                                              motivos_negacao):
    endpoint_detalhe(
        client_autenticado,
        ENDPOINT_MOTIVOS_NEGACAO,
        MotivoNegacao
    )


def test_url_endpoint_detalhe_tipos_dieta(client_autenticado,
                                          tipos_dieta):
    endpoint_detalhe(
        client_autenticado,
        ENDPOINT_TIPOS_DIETA_ESPECIAL,
        TipoDieta
    )


def test_url_endpoint_autoriza_dieta(client_autenticado,
                                     solicitacao_dieta_especial_a_autorizar,
                                     alergias_intolerancias,
                                     classificacoes_dieta):
    obj = SolicitacaoDietaEspecial.objects.first()
    data = {
        'classificacao': classificacoes_dieta[0].id,
        'alergias_intolerancias': [
            alergias_intolerancias[0].id
        ],
        'registro_funcional_nutricionista':
            'ELABORADO por USUARIO NUTRICIONISTA CODAE - CRN null',
        'protocolos': [
            {
                'nome': 'Teste',
                'base64': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAaQAAAGkCAIAAADxLsZiAAAFyklEQVR4nOzWUZHbYBA' +
                          'GwThlHsYmEEIhEMImBgshJHL6rZtuAvs9Te17Zv4A/HZ/Vw8AuIPYAQliBySIHZAgdkCC2AEJYgckiB2QIHZAgtgB' +
                          'CWIHJIgdkCB2QILYAQliBySIHZAgdkCC2AEJYgckiB2QIHZAgtgBCWIHJIgdkCB2QILYAQliBySIHZAgdkCC2AEJY' +
                          'gckiB2QIHZAgtgBCe/VAx7svI7VEyjaPvvqCY/kswMSxA5IEDsgQeyABLEDEsQOSBA7IEHsgASxAxLEDkgQOyBB7I' +
                          'AEsQMSxA5IEDsgQeyABLEDEsQOSBA7IEHsgASxAxLEDkgQOyBB7IAEsQMSxA5IEDsgQeyABLEDEsQOSBA7IEHsgAS' +
                          'xAxLEDkgQOyBB7IAEsQMSxA5IEDsgQeyABLEDEsQOSBA7IEHsgASxAxLEDkgQOyBB7IAEsQMSxA5IEDsgQeyABLED' +
                          'EsQOSBA7IEHsgASxAxLEDkgQOyBB7IAEsQMSxA5IEDsgQeyABLEDEsQOSBA7IEHsgASxAxJeM3PPpfM67jkEPMv22' +
                          'W+44rMDEsQOSBA7IEHsgASxAxLEDkgQOyBB7IAEsQMSxA5IEDsgQeyABLEDEsQOSBA7IEHsgASxAxLEDkgQOyBB7I' +
                          'AEsQMSxA5IEDsgQeyABLEDEsQOSBA7IEHsgASxAxLEDkgQOyBB7IAEsQMSxA5IEDsgQeyABLEDEsQOSBA7IEHsgAS' +
                          'xAxLEDkgQOyBB7IAEsQMSxA5IEDsgQeyABLEDEsQOSBA7IEHsgASxAxLEDkgQOyBB7IAEsQMSxA5IEDsgQeyABLED' +
                          'EsQOSBA7IEHsgASxAxLEDkgQOyBB7IAEsQMSxA5IeM3M6g1PdV7H6gkUbZ999YRH8tkBCWIHJIgdkCB2QILYAQliB' +
                          'ySIHZAgdkCC2AEJYgckiB2QIHZAgtgBCWIHJIgdkCB2QILYAQliBySIHZAgdkCC2AEJYgckiB2QIHZAgtgBCWIHJI' +
                          'gdkCB2QILYAQliBySIHZAgdkCC2AEJYgckiB2QIHZAgtgBCWIHJIgdkCB2QILYAQliBySIHZAgdkCC2AEJYgckiB2' +
                          'QIHZAgtgBCWIHJIgdkCB2QILYAQliBySIHZAgdkCC2AEJYgckiB2QIHZAgtgBCWIHJIgdkCB2QILYAQliBySIHZAg' +
                          'dkCC2AEJr5lZvQHgx/nsgASxAxLEDkgQOyBB7IAEsQMSxA5IEDsgQeyABLEDEsQOSBA7IEHsgASxAxLEDkgQOyBB7' +
                          'IAEsQMSxA5IEDsgQeyABLEDEsQOSBA7IEHsgASxAxLEDkgQOyBB7IAEsQMSxA5IEDsgQeyABLEDEsQOSBA7IEHsgA' +
                          'SxAxLEDkgQOyBB7IAEsQMSxA5IEDsgQeyABLEDEsQOSBA7IEHsgASxAxLEDkgQOyBB7IAEsQMSxA5IEDsgQeyABLE' +
                          'DEsQOSBA7IEHsgASxAxLEDkgQOyBB7IAEsQMSxA5IEDsg4b16AF/kvI7VE/6/7bOvnsBX8NkBCWIHJIgdkCB2QILY' +
                          'AQliBySIHZAgdkCC2AEJYgckiB2QIHZAgtgBCWIHJIgdkCB2QILYAQliBySIHZAgdkCC2AEJYgckiB2QIHZAgtgBC' +
                          'WIHJIgdkCB2QILYAQliBySIHZAgdkCC2AEJYgckiB2QIHZAgtgBCWIHJIgdkCB2QILYAQliBySIHZAgdkCC2AEJYg' +
                          'ckiB2QIHZAgtgBCWIHJIgdkCB2QILYAQliBySIHZAgdkCC2AEJYgckiB2QIHZAgtgBCWIHJIgdkCB2QILYAQliByS' +
                          'IHZAgdkCC2AEJYgckvGZm9QaAH+ezAxLEDkgQOyBB7IAEsQMSxA5IEDsgQeyABLEDEsQOSBA7IEHsgASxAxLEDkgQ' +
                          'OyBB7IAEsQMSxA5IEDsgQeyABLEDEsQOSBA7IEHsgASxAxLEDkgQOyBB7IAEsQMSxA5IEDsgQeyABLEDEv4FAAD//' +
                          'xmNHVuA/EwlAAAAAElFTkSuQmCC'
            }
        ]
    }
    response = client_autenticado.post(
        f'/solicitacoes-dieta-especial/{obj.uuid}/autoriza/',
        content_type='application/json',
        data=data
    )

    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json['mensagem'] == 'Autorização de dieta especial realizada com sucesso'

    obj.refresh_from_db()

    assert obj.status == DietaEspecialWorkflow.CODAE_AUTORIZADO
    assert obj.registro_funcional_nutricionista == data['registro_funcional_nutricionista']
    for ai in obj.alergias_intolerancias.all():
        assert ai.id in data['alergias_intolerancias']
    assert obj.classificacao.id == data['classificacao']

    anexos = Anexo.objects.filter(solicitacao_dieta_especial=obj)
    assert anexos.count() == 1


def test_url_endpoint_nega_dieta(client_autenticado,
                                 solicitacao_dieta_especial_a_autorizar,
                                 motivos_negacao):
    obj = SolicitacaoDietaEspecial.objects.first()
    data = {
        'justificativa_negacao': 'Uma justificativa fajuta',
        'motivo_negacao': motivos_negacao[0].id
    }
    response = client_autenticado.post(
        f'/solicitacoes-dieta-especial/{obj.uuid}/negar/',
        content_type='application/json',
        data=data
    )

    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json['mensagem'] == 'Solicitação de Dieta Especial Negada'

    obj.refresh_from_db()

    assert obj.status == DietaEspecialWorkflow.CODAE_NEGOU_PEDIDO
    assert obj.justificativa_negacao == data['justificativa_negacao']
    assert obj.motivo_negacao.id == data['motivo_negacao']
