import datetime

import pytest
from faker import Faker
from model_mommy import mommy

from .. import models
from ...dados_comuns.behaviors import TempoPasseio
from ...dados_comuns.fluxo_status import PedidoAPartirDaDiretoriaRegionalWorkflow, PedidoAPartirDaEscolaWorkflow
from ...dados_comuns.models import TemplateMensagem

fake = Faker('pt_BR')
fake.seed(420)


@pytest.fixture
def escola():
    lote = mommy.make('Lote')
    return mommy.make('Escola', lote=lote)


@pytest.fixture
def kit_lanche():
    itens = mommy.make(models.ItemKitLanche,
                       nome=fake.name(),
                       _quantity=3)
    return mommy.make(models.KitLanche, nome=fake.name(),
                      itens=itens)


@pytest.fixture
def item_kit_lanche():
    return mommy.make(models.ItemKitLanche,
                      nome=fake.name())


@pytest.fixture
def solicitacao_avulsa(escola):
    mommy.make(TemplateMensagem, tipo=TemplateMensagem.SOLICITACAO_KIT_LANCHE_AVULSA)
    kits = mommy.make(models.KitLanche, _quantity=3)
    solicitacao_kit_lanche = mommy.make(models.SolicitacaoKitLanche, kits=kits, data=datetime.datetime(2000, 1, 1))
    return mommy.make(models.SolicitacaoKitLancheAvulsa,
                      local=fake.text()[:160],
                      quantidade_alunos=999,
                      solicitacao_kit_lanche=solicitacao_kit_lanche,
                      escola=escola)


@pytest.fixture
def solicitacao_avulsa_dre_a_validar(solicitacao_avulsa, escola):
    solicitacao_avulsa = mommy.make('SolicitacaoKitLancheAvulsa',
                                    status=PedidoAPartirDaEscolaWorkflow.DRE_A_VALIDAR,
                                    escola=escola)
    return solicitacao_avulsa


@pytest.fixture
def solicitacao_avulsa_dre_validado(solicitacao_avulsa, escola):
    solicitacao_avulsa = mommy.make('SolicitacaoKitLancheAvulsa',
                                    status=PedidoAPartirDaEscolaWorkflow.DRE_VALIDADO,
                                    escola=escola)
    return solicitacao_avulsa


@pytest.fixture
def solicitacao_avulsa_codae_autorizado(solicitacao_avulsa, escola):
    solicitacao_kit_lanche = mommy.make(models.SolicitacaoKitLanche, data=datetime.datetime(2019, 11, 18))
    solicitacao_avulsa = mommy.make('SolicitacaoKitLancheAvulsa',
                                    solicitacao_kit_lanche=solicitacao_kit_lanche,
                                    status=PedidoAPartirDaEscolaWorkflow.CODAE_AUTORIZADO,
                                    escola=escola)
    return solicitacao_avulsa


@pytest.fixture
def solicitacao_unificada_lista_igual(escola):
    mommy.make(TemplateMensagem, tipo=TemplateMensagem.SOLICITACAO_KIT_LANCHE_UNIFICADA)
    kits = mommy.make(models.KitLanche, _quantity=3)
    solicitacao_kit_lanche = mommy.make(models.SolicitacaoKitLanche,
                                        data=datetime.date(2019, 10, 14),
                                        tempo_passeio=models.SolicitacaoKitLanche.OITO_OU_MAIS,
                                        kits=kits)
    escolas_quantidades = mommy.make('EscolaQuantidade', escola=escola, _quantity=10, quantidade_alunos=100)
    dre = mommy.make('escola.DiretoriaRegional')
    solicitacao_unificada = mommy.make(models.SolicitacaoKitLancheUnificada,
                                       local=fake.text()[:160],
                                       lista_kit_lanche_igual=True,
                                       solicitacao_kit_lanche=solicitacao_kit_lanche,
                                       outro_motivo=fake.text(),
                                       diretoria_regional=dre)
    solicitacao_unificada.escolas_quantidades.set(escolas_quantidades)
    return solicitacao_unificada


@pytest.fixture
def solicitacao_unificada_lotes_diferentes():
    kits = mommy.make(models.KitLanche, _quantity=3)
    solicitacao_kit_lanche = mommy.make(models.SolicitacaoKitLanche,
                                        tempo_passeio=models.SolicitacaoKitLanche.OITO_OU_MAIS,
                                        kits=kits)
    dre = mommy.make('escola.DiretoriaRegional', nome=fake.name())
    solicitacao_unificada = mommy.make(models.SolicitacaoKitLancheUnificada,
                                       local=fake.text()[:160],
                                       lista_kit_lanche_igual=True,
                                       solicitacao_kit_lanche=solicitacao_kit_lanche,
                                       outro_motivo=fake.text(),
                                       diretoria_regional=dre)
    lote_um = mommy.make('escola.Lote')
    escola_um = mommy.make('escola.Escola', lote=lote_um)
    escola_dois = mommy.make('escola.Escola', lote=lote_um)
    escola_tres = mommy.make('escola.Escola', lote=lote_um)
    mommy.make(models.EscolaQuantidade,
               escola=escola_um,
               solicitacao_unificada=solicitacao_unificada)
    mommy.make(models.EscolaQuantidade,
               escola=escola_dois,
               solicitacao_unificada=solicitacao_unificada)
    mommy.make(models.EscolaQuantidade,
               escola=escola_tres,
               solicitacao_unificada=solicitacao_unificada)
    lote_dois = mommy.make('escola.Lote')
    escola_quatro = mommy.make('escola.Escola', lote=lote_dois)
    escola_cinco = mommy.make('escola.Escola', lote=lote_dois)
    mommy.make(models.EscolaQuantidade,
               escola=escola_quatro,
               solicitacao_unificada=solicitacao_unificada)
    mommy.make(models.EscolaQuantidade,
               escola=escola_cinco,
               solicitacao_unificada=solicitacao_unificada)
    return solicitacao_unificada


@pytest.fixture
def solicitacao_unificada_lotes_iguais():
    kits = mommy.make(models.KitLanche, _quantity=3)
    solicitacao_kit_lanche = mommy.make(models.SolicitacaoKitLanche,
                                        tempo_passeio=models.SolicitacaoKitLanche.OITO_OU_MAIS,
                                        kits=kits)
    dre = mommy.make('escola.DiretoriaRegional', nome=fake.name())
    solicitacao_unificada = mommy.make(models.SolicitacaoKitLancheUnificada,
                                       local=fake.text()[:160],
                                       lista_kit_lanche_igual=True,
                                       solicitacao_kit_lanche=solicitacao_kit_lanche,
                                       outro_motivo=fake.text(),
                                       diretoria_regional=dre)
    lote_um = mommy.make('escola.Lote')
    escola_um = mommy.make('escola.Escola', lote=lote_um)
    escola_dois = mommy.make('escola.Escola', lote=lote_um)
    escola_tres = mommy.make('escola.Escola', lote=lote_um)
    escola_quatro = mommy.make('escola.Escola', lote=lote_um)
    escola_cinco = mommy.make('escola.Escola', lote=lote_um)
    mommy.make(models.EscolaQuantidade,
               escola=escola_um,
               solicitacao_unificada=solicitacao_unificada)
    mommy.make(models.EscolaQuantidade,
               escola=escola_dois,
               solicitacao_unificada=solicitacao_unificada)
    mommy.make(models.EscolaQuantidade,
               escola=escola_tres,
               solicitacao_unificada=solicitacao_unificada)
    mommy.make(models.EscolaQuantidade,
               escola=escola_quatro,
               solicitacao_unificada=solicitacao_unificada)
    mommy.make(models.EscolaQuantidade,
               escola=escola_cinco,
               solicitacao_unificada=solicitacao_unificada)
    return solicitacao_unificada


@pytest.fixture
def solicitacao():
    kits = mommy.make(models.KitLanche, nome=fake.name(), _quantity=3)
    return mommy.make(models.SolicitacaoKitLanche,
                      descricao=fake.text(),
                      motivo=fake.text(),
                      tempo_passeio=TempoPasseio.CINCO_A_SETE,
                      kits=kits)


@pytest.fixture(params=[
    (0, True),
    (1, True),
    (2, True),
])
def horarios_passeio(request):
    return request.param


erro_esperado_passeio = 'tempo de passeio deve ser qualquer uma das opções:'


@pytest.fixture(params=[
    ('0', erro_esperado_passeio),
    ('TESTE', erro_esperado_passeio),
    (3, erro_esperado_passeio),
])
def horarios_passeio_invalido(request):
    return request.param


@pytest.fixture(params=[
    # tempo passeio, qtd kits
    (0, 1),
    (1, 2),
    (2, 3),
])
def tempo_kits(request):
    return request.param


@pytest.fixture(params=[
    # para testar no dia 2/10/19
    # data do evento, tag
    (datetime.date(2019, 9, 30), 'VENCIDO'),
    (datetime.date(2019, 10, 1), 'VENCIDO'),
    (datetime.date(2019, 10, 2), 'PRIORITARIO'),
    (datetime.date(2019, 10, 3), 'PRIORITARIO'),
    (datetime.date(2019, 10, 4), 'PRIORITARIO'),
    (datetime.date(2019, 10, 5), 'PRIORITARIO'),
    (datetime.date(2019, 10, 6), 'PRIORITARIO'),
    (datetime.date(2019, 10, 7), 'LIMITE'),
    (datetime.date(2019, 10, 8), 'LIMITE'),
    (datetime.date(2019, 10, 9), 'LIMITE'),
    (datetime.date(2019, 10, 10), 'REGULAR'),
    (datetime.date(2019, 10, 11), 'REGULAR'),
    (datetime.date(2019, 10, 12), 'REGULAR'),
    (datetime.date(2019, 10, 13), 'REGULAR'),
])
def kits_avulsos_parametros(request):
    return request.param


@pytest.fixture(params=[
    # para testar no dia 20/12/19
    # data do evento, tag
    (datetime.date(2019, 12, 18), 'VENCIDO'),
    (datetime.date(2019, 12, 19), 'VENCIDO'),
    (datetime.date(2019, 12, 20), 'PRIORITARIO'),
    (datetime.date(2019, 12, 21), 'PRIORITARIO'),
    (datetime.date(2019, 12, 22), 'PRIORITARIO'),
    (datetime.date(2019, 12, 23), 'PRIORITARIO'),
    (datetime.date(2019, 12, 24), 'PRIORITARIO'),
    (datetime.date(2019, 12, 25), 'PRIORITARIO'),
    (datetime.date(2019, 12, 26), 'LIMITE'),
    (datetime.date(2019, 12, 27), 'LIMITE'),
    (datetime.date(2019, 12, 28), 'LIMITE'),
    (datetime.date(2019, 12, 29), 'LIMITE'),
    (datetime.date(2019, 12, 30), 'LIMITE'),
    (datetime.date(2019, 12, 31), 'REGULAR'),
    (datetime.date(2020, 1, 1), 'REGULAR')
])
def kits_avulsos_parametros2(request):
    return request.param


@pytest.fixture(params=[
    # para testar no dia 3/10/19
    # data do evento, status
    (datetime.date(2019, 10, 2), PedidoAPartirDaEscolaWorkflow.RASCUNHO),
    (datetime.date(2019, 10, 1), PedidoAPartirDaEscolaWorkflow.DRE_VALIDADO),
    (datetime.date(2019, 9, 30), PedidoAPartirDaEscolaWorkflow.DRE_PEDIU_ESCOLA_REVISAR),
    (datetime.date(2019, 9, 29), PedidoAPartirDaEscolaWorkflow.DRE_VALIDADO),
    (datetime.date(2019, 9, 28), PedidoAPartirDaEscolaWorkflow.DRE_VALIDADO),
    (datetime.date(2019, 9, 27), PedidoAPartirDaEscolaWorkflow.RASCUNHO),
    (datetime.date(2019, 9, 26), PedidoAPartirDaEscolaWorkflow.DRE_PEDIU_ESCOLA_REVISAR),
])
def kits_avulsos_datas_passado_parametros(request):
    return request.param


@pytest.fixture(params=[
    # para testar no dia 3/10/19
    (datetime.date(2019, 10, 3)),
    (datetime.date(2019, 10, 4)),
    (datetime.date(2019, 10, 5)),
    (datetime.date(2019, 10, 6)),
    (datetime.date(2019, 10, 7)),
    (datetime.date(2019, 10, 8)),
    (datetime.date(2019, 10, 9)),
    (datetime.date(2019, 10, 10)),
])
def kits_avulsos_datas_semana(request):
    return request.param


@pytest.fixture(params=[
    # para testar no dia 3/10/19
    (datetime.date(2019, 10, 3)),
    (datetime.date(2019, 10, 8)),
    (datetime.date(2019, 10, 10)),
    (datetime.date(2019, 10, 15)),
    (datetime.date(2019, 10, 20)),
    (datetime.date(2019, 11, 3)),
])
def kits_avulsos_datas_mes(request):
    return request.param


@pytest.fixture(params=[
    # para testar no dia 3/10/19
    # data do evento, status
    (datetime.date(2019, 10, 2), PedidoAPartirDaDiretoriaRegionalWorkflow.RASCUNHO),
    (datetime.date(2019, 10, 1), PedidoAPartirDaDiretoriaRegionalWorkflow.CODAE_A_AUTORIZAR),
    (datetime.date(2019, 9, 30), PedidoAPartirDaDiretoriaRegionalWorkflow.CODAE_PEDIU_DRE_REVISAR),
    (datetime.date(2019, 9, 29), PedidoAPartirDaDiretoriaRegionalWorkflow.RASCUNHO),
    (datetime.date(2019, 9, 28), PedidoAPartirDaDiretoriaRegionalWorkflow.CODAE_PEDIU_DRE_REVISAR),
    (datetime.date(2019, 9, 27), PedidoAPartirDaDiretoriaRegionalWorkflow.CODAE_A_AUTORIZAR),
    (datetime.date(2019, 9, 26), PedidoAPartirDaDiretoriaRegionalWorkflow.CODAE_PEDIU_DRE_REVISAR),
])
def kits_unificados_datas_passado_parametros(request):
    return request.param


@pytest.fixture(params=[
    # qtd_alunos_escola, qtd_alunos_pedido, dia, confirmar??? TODO ver esse confirmar... erro esperado
    (100, 101, datetime.date(2019, 10, 18), True,
     'A quantidade de alunos informados para o evento excede a quantidade de alunos matriculados na escola'),
    (100, 100, datetime.date(2001, 1, 1), True, 'Não pode ser no passado'),
    (100, 99, datetime.date(2019, 10, 16), False, 'Deve pedir com pelo menos 2 dias úteis de antecedência'),
    (100, 99, datetime.date(2019, 10, 16), True, 'Deve pedir com pelo menos 2 dias úteis de antecedência'),
    (100, 99, datetime.date(2019, 10, 17), True, 'Deve pedir com pelo menos 2 dias úteis de antecedência'),
    (100, 400, datetime.date(2019, 10, 18), False,
     'A quantidade de alunos informados para o evento excede a quantidade de alunos matriculados na escola'),
])
def kits_avulsos_param_erro_serializer(request):
    return request.param


@pytest.fixture(params=[
    # qtd_alunos_escola, qtd_alunos_pedido, dia
    (100, 100, datetime.date(2020, 1, 1)),
    (1000, 77, datetime.date(2019, 10, 20)),
    (1000, 700, datetime.date(2019, 10, 20)),
])
def kits_avulsos_param_serializer(request):
    return request.param


@pytest.fixture(params=[
    # qtd_alunos_escola, qtd_alunos_pedido, dia
    (100, 100, datetime.date(2020, 1, 1)),
    (1000, 77, datetime.date(2019, 10, 20)),
    (1000, 700, datetime.date(2019, 10, 20)),
])
def kits_unificados_param_serializer(request):
    return request.param


@pytest.fixture
def escola_quantidade():
    return mommy.make(models.EscolaQuantidade)
