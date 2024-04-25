from datetime import date, timedelta

import pytest
from faker import Faker

from sme_terceirizadas.dados_comuns.fluxo_status import (
    DocumentoDeRecebimentoWorkflow,
    FichaTecnicaDoProdutoWorkflow,
)
from sme_terceirizadas.recebimento.models import QuestaoConferencia

fake = Faker("pt_BR")


@pytest.fixture
def questoes_conferencia(questao_conferencia_factory):
    return questao_conferencia_factory.create_batch(
        size=10,
        tipo_questao=[
            QuestaoConferencia.TIPO_QUESTAO_PRIMARIA,
            QuestaoConferencia.TIPO_QUESTAO_SECUNDARIA,
        ],
    )


@pytest.fixture
def payload_create_questoes_por_produto(
    ficha_tecnica_factory,
    questoes_conferencia,
):
    questoes = [str(q.uuid) for q in questoes_conferencia]

    return {
        "ficha_tecnica": str(
            ficha_tecnica_factory(status=FichaTecnicaDoProdutoWorkflow.APROVADA).uuid
        ),
        "questoes_primarias": questoes,
        "questoes_secundarias": questoes,
    }


@pytest.fixture
def payload_update_questoes_por_produto(questoes_conferencia):
    questoes = [str(q.uuid) for q in questoes_conferencia]

    return {
        "questoes_primarias": questoes,
        "questoes_secundarias": questoes,
    }


@pytest.fixture
def payload_ficha_recebimento_rascunho(
    etapas_do_cronograma_factory,
    documento_de_recebimento_factory,
):
    etapa = etapas_do_cronograma_factory()
    docs_recebimento = documento_de_recebimento_factory.create_batch(
        size=3,
        cronograma=etapa.cronograma,
        status=DocumentoDeRecebimentoWorkflow.APROVADO,
    )

    return {
        "etapa": str(etapa.uuid),
        "data_entrega": str(date.today() + timedelta(days=10)),
        "laudos": [doc.numero_laudo for doc in docs_recebimento],
        "lote_fabricante_de_acordo": True,
        "lote_fabricante_divergencia": "",
        "data_fabricacao_de_acordo": True,
        "data_fabricacao_divergencia": "",
        "data_validade_de_acordo": True,
        "data_validade_divergencia": "",
        "numero_lote_armazenagem": str(fake.random_number(digits=10)),
        "numero_paletes": str(fake.random_number(digits=3)),
        "peso_embalagem_primaria_1": str(fake.random_number(digits=3)),
        "peso_embalagem_primaria_2": str(fake.random_number(digits=3)),
        "peso_embalagem_primaria_3": str(fake.random_number(digits=3)),
        "peso_embalagem_primaria_4": str(fake.random_number(digits=3)),
        "veiculos": [
            {
                "numero": "Veiculo 1",
                "temperatura_recebimento": str(fake.random_number(digits=3)),
                "temperatura_produto": str(fake.random_number(digits=3)),
                "placa": str(fake.random_number(digits=7)),
                "lacre": str(fake.random_number(digits=7)),
                "numero_sif_sisbi_sisp": str(fake.random_number(digits=10)),
                "numero_nota_fiscal": str(fake.random_number(digits=44)),
                "quantidade_nota_fiscal": "1234",
                "embalagens_nota_fiscal": "12",
                "quantidade_recebida": "1234",
                "embalagens_recebidas": "12",
                "estado_higienico_adequado": True,
                "termografo": True,
            },
            {
                "numero": "Veiculo 2",
                "temperatura_recebimento": str(fake.random_number(digits=3)),
                "temperatura_produto": str(fake.random_number(digits=3)),
                "placa": str(fake.random_number(digits=7)),
                "lacre": str(fake.random_number(digits=7)),
                "numero_sif_sisbi_sisp": str(fake.random_number(digits=10)),
                "numero_nota_fiscal": str(fake.random_number(digits=44)),
                "quantidade_nota_fiscal": "1234",
                "embalagens_nota_fiscal": "12",
                "quantidade_recebida": "1234",
                "embalagens_recebidas": "12",
                "estado_higienico_adequado": True,
                "termografo": True,
            },
        ],
    }
