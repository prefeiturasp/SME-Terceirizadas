import datetime

from django.template.loader import render_to_string

from ..dados_comuns.fluxo_status import ReclamacaoProdutoWorkflow
from ..dados_comuns.models import LogSolicitacoesUsuario
from ..kit_lanche.models import EscolaQuantidade
from ..relatorios.utils import html_to_pdf_response
from ..terceirizada.utils import transforma_dados_relatorio_quantitativo
from . import constants
from .utils import (
    conta_filtros,
    formata_logs,
    get_config_cabecario_relatorio_analise,
    get_diretorias_regionais,
    get_width
)


def relatorio_filtro_periodo(request, query_set_consolidado, escola_nome='', dre_nome=''):
    # TODO: se query_set_consolidado tiver muitos resultados, pode demorar no front-end
    # melhor mandar via celery pro email de quem solicitou
    # ou por padrão manda tudo pro celery
    request_params = request.GET

    tipo_solicitacao = request_params.get('tipo_solicitacao', 'INVALIDO')
    status_solicitacao = request_params.get('status_solicitacao', 'INVALIDO')
    data_inicial = datetime.datetime.strptime(request_params.get('data_inicial'), '%Y-%m-%d')
    data_final = datetime.datetime.strptime(request_params.get('data_final'), '%Y-%m-%d')
    filtro = {'tipo_solicitacao': tipo_solicitacao, 'status': status_solicitacao,
              'data_inicial': data_inicial, 'data_final': data_final}

    html_string = render_to_string(
        'relatorio_filtro.html',
        {
            'diretoria_regional_nome': dre_nome, 'escola_nome': escola_nome, 'filtro': filtro,
            'query_set_consolidado': query_set_consolidado
        }
    )
    return html_to_pdf_response(html_string, f'relatorio_filtro_de_{data_inicial}_ate_{data_final}.pdf')


def relatorio_resumo_anual_e_mensal(request, resumos_mes, resumo_ano):
    meses = range(12)
    escola_nome = 'ESCOLA'
    dre_nome = 'DRE'
    filtro = {'tipo_solicitacao': 'TODOS', 'status': 'TODOS',
              'data_inicial': 'data_inicial', 'data_final': 'data_final'}

    html_string = render_to_string(
        'relatorio_resumo_mes_ano.html',
        {
            'diretoria_regional_nome': dre_nome, 'escola_nome': escola_nome, 'filtro': filtro,
            'resumos_mes': resumos_mes, 'resumo_ano': resumo_ano, 'meses': meses
        }
    )
    return html_to_pdf_response(html_string, f'relatorio_resumo_anual_e_mensal.pdf')


def relatorio_kit_lanche_unificado(request, solicitacao):
    qtd_escolas = EscolaQuantidade.objects.filter(solicitacao_unificada=solicitacao).count()

    html_string = render_to_string(
        'solicitacao_kit_lanche_unificado.html',
        {'solicitacao': solicitacao, 'qtd_escolas': qtd_escolas,
         'fluxo': constants.FLUXO_PARTINDO_DRE,
         'width': get_width(constants.FLUXO_PARTINDO_DRE, solicitacao.logs),
         'logs': formata_logs(solicitacao.logs)}
    )
    return html_to_pdf_response(html_string, f'solicitacao_unificada_{solicitacao.id_externo}.pdf')


def relatorio_alteracao_cardapio(request, solicitacao):
    escola = solicitacao.rastro_escola
    substituicoes = solicitacao.substituicoes_periodo_escolar
    logs = solicitacao.logs
    html_string = render_to_string(
        'solicitacao_alteracao_cardapio.html',
        {'escola': escola,
         'solicitacao': solicitacao,
         'substituicoes': substituicoes,
         'fluxo': constants.FLUXO_PARTINDO_ESCOLA,
         'width': get_width(constants.FLUXO_PARTINDO_ESCOLA, solicitacao.logs),
         'logs': formata_logs(logs)}
    )
    return html_to_pdf_response(html_string, f'alteracao_cardapio_{solicitacao.id_externo}.pdf')


def relatorio_alteracao_cardapio_cei(request, solicitacao):
    escola = solicitacao.rastro_escola
    substituicoes = solicitacao.substituicoes_cei_periodo_escolar
    logs = solicitacao.logs
    html_string = render_to_string(
        'solicitacao_alteracao_cardapio_cei.html',
        {'escola': escola,
         'solicitacao': solicitacao,
         'substituicoes': substituicoes,
         'fluxo': constants.FLUXO_PARTINDO_ESCOLA,
         'width': get_width(constants.FLUXO_PARTINDO_ESCOLA, solicitacao.logs),
         'logs': formata_logs(logs)}
    )
    return html_to_pdf_response(html_string, f'alteracao_cardapio_{solicitacao.id_externo}.pdf')


def relatorio_dieta_especial(request, solicitacao):
    escola = solicitacao.rastro_escola
    logs = solicitacao.logs
    if solicitacao.logs.filter(status_evento=LogSolicitacoesUsuario.INICIO_FLUXO_INATIVACAO).exists():
        if solicitacao.logs.filter(status_evento=LogSolicitacoesUsuario.TERCEIRIZADA_TOMOU_CIENCIA).exists():
            fluxo = constants.FLUXO_DIETA_ESPECIAL_INATIVACAO
        else:
            fluxo = constants.FLUXO_DIETA_ESPECIAL_INATIVACAO_INCOMPLETO
    else:
        fluxo = constants.FLUXO_DIETA_ESPECIAL
    html_string = render_to_string(
        'solicitacao_dieta_especial.html',
        {
            'escola': escola,
            'solicitacao': solicitacao,
            'fluxo': fluxo,
            'width': get_width(fluxo, solicitacao.logs),
            'logs': formata_logs(logs)
        }
    )
    return html_to_pdf_response(html_string, f'dieta_especial_{solicitacao.id_externo}.pdf')


def relatorio_dieta_especial_protocolo(request, solicitacao):
    html_string = render_to_string(
        'solicitacao_dieta_especial_protocolo.html',
        {
            'escola': solicitacao.rastro_escola,
            'solicitacao': solicitacao,
            'data_termino': solicitacao.data_termino,
            'log_autorizacao': solicitacao.logs.get(status_evento=LogSolicitacoesUsuario.CODAE_AUTORIZOU)
        }
    )
    return html_to_pdf_response(html_string, f'dieta_especial_{solicitacao.id_externo}.pdf')


def relatorio_inclusao_alimentacao_continua(request, solicitacao):
    escola = solicitacao.rastro_escola
    logs = solicitacao.logs
    html_string = render_to_string(
        'solicitacao_inclusao_alimentacao_continua.html',
        {
            'escola': escola,
            'solicitacao': solicitacao,
            'fluxo': constants.FLUXO_PARTINDO_ESCOLA,
            'width': get_width(constants.FLUXO_PARTINDO_ESCOLA, solicitacao.logs),
            'logs': formata_logs(logs)
        }
    )
    return html_to_pdf_response(html_string, f'inclusao_alimentacao_continua_{solicitacao.id_externo}.pdf')


def relatorio_inclusao_alimentacao_normal(request, solicitacao):
    escola = solicitacao.rastro_escola
    logs = solicitacao.logs
    html_string = render_to_string(
        'solicitacao_inclusao_alimentacao_normal.html',
        {
            'escola': escola,
            'solicitacao': solicitacao,
            'fluxo': constants.FLUXO_PARTINDO_ESCOLA,
            'width': get_width(constants.FLUXO_PARTINDO_ESCOLA, solicitacao.logs),
            'logs': formata_logs(logs)
        }
    )
    return html_to_pdf_response(html_string, f'inclusao_alimentacao_{solicitacao.id_externo}.pdf')


def relatorio_inclusao_alimentacao_cei(request, solicitacao):
    escola = solicitacao.rastro_escola
    logs = solicitacao.logs
    html_string = render_to_string(
        'solicitacao_inclusao_alimentacao_cei.html',
        {
            'escola': escola,
            'solicitacao': solicitacao,
            'fluxo': constants.FLUXO_PARTINDO_ESCOLA,
            'width': get_width(constants.FLUXO_PARTINDO_ESCOLA, solicitacao.logs),
            'logs': formata_logs(logs)
        }
    )
    return html_to_pdf_response(html_string, f'inclusao_alimentacao_{solicitacao.id_externo}.pdf')


def relatorio_kit_lanche_passeio(request, solicitacao):
    escola = solicitacao.rastro_escola
    logs = solicitacao.logs
    observacao = solicitacao.solicitacao_kit_lanche.descricao
    solicitacao.observacao = observacao
    html_string = render_to_string(
        'solicitacao_kit_lanche_passeio.html',
        {
            'escola': escola,
            'solicitacao': solicitacao,
            'quantidade_kits': solicitacao.solicitacao_kit_lanche.kits.all().count() * solicitacao.quantidade_alunos,
            'fluxo': constants.FLUXO_PARTINDO_ESCOLA,
            'width': get_width(constants.FLUXO_PARTINDO_ESCOLA, solicitacao.logs),
            'logs': formata_logs(logs)
        }
    )
    return html_to_pdf_response(html_string, f'solicitacao_avulsa_{solicitacao.id_externo}.pdf')


def relatorio_kit_lanche_passeio_cei(request, solicitacao):
    escola = solicitacao.rastro_escola
    logs = solicitacao.logs
    observacao = solicitacao.solicitacao_kit_lanche.descricao
    solicitacao.observacao = observacao
    html_string = render_to_string(
        'solicitacao_kit_lanche_passeio_cei.html',
        {
            'escola': escola,
            'solicitacao': solicitacao,
            'quantidade_kits': solicitacao.solicitacao_kit_lanche.kits.all().count() * solicitacao.quantidade_alunos,
            'fluxo': constants.FLUXO_PARTINDO_ESCOLA,
            'width': get_width(constants.FLUXO_PARTINDO_ESCOLA, solicitacao.logs),
            'logs': formata_logs(logs)
        }
    )
    return html_to_pdf_response(html_string, f'solicitacao_avulsa_{solicitacao.id_externo}.pdf')


def relatorio_inversao_dia_de_cardapio(request, solicitacao):
    escola = solicitacao.rastro_escola
    logs = solicitacao.logs
    html_string = render_to_string(
        'solicitacao_inversao_de_cardapio.html',
        {
            'escola': escola,
            'solicitacao': solicitacao,
            'data_de': solicitacao.cardapio_de.data,
            'data_para': solicitacao.cardapio_para.data,
            'fluxo': constants.FLUXO_PARTINDO_ESCOLA,
            'width': get_width(constants.FLUXO_PARTINDO_ESCOLA, solicitacao.logs),
            'logs': formata_logs(logs)
        }
    )
    return html_to_pdf_response(html_string, f'solicitacao_inversao_{solicitacao.id_externo}.pdf')


def relatorio_suspensao_de_alimentacao(request, solicitacao):
    escola = solicitacao.rastro_escola
    logs = solicitacao.logs
    # TODO: GrupoSuspensaoAlimentacaoSerializerViewSet não tem motivo, quem tem é cada suspensão do relacionamento
    motivo = 'Deve ajustar aqui...'
    suspensoes = solicitacao.suspensoes_alimentacao.all()
    quantidades_por_periodo = solicitacao.quantidades_por_periodo.all()
    html_string = render_to_string(
        'solicitacao_suspensao_de_alimentacao.html',
        {
            'escola': escola,
            'solicitacao': solicitacao,
            'suspensoes': suspensoes,
            'motivo': motivo,
            'quantidades_por_periodo': quantidades_por_periodo,
            'fluxo': constants.FLUXO_INFORMATIVO,
            'width': get_width(constants.FLUXO_INFORMATIVO, solicitacao.logs),
            'logs': formata_logs(logs)
        }
    )
    return html_to_pdf_response(html_string, f'solicitacao_suspensao_{solicitacao.id_externo}.pdf')


def relatorio_produto_homologacao(request, produto):
    homologacao = produto.homologacoes.first()
    terceirizada = homologacao.rastro_terceirizada
    reclamacao = homologacao.reclamacoes.filter(
        status=ReclamacaoProdutoWorkflow.CODAE_ACEITOU).first()
    logs = homologacao.logs
    lotes = terceirizada.lotes.all()
    html_string = render_to_string(
        'homologacao_produto.html',
        {
            'terceirizada': terceirizada,
            'reclamacao': reclamacao,
            'homologacao': homologacao,
            'fluxo': constants.FLUXO_HOMOLOGACAO_PRODUTO,
            'width': get_width(constants.FLUXO_HOMOLOGACAO_PRODUTO, logs),
            'produto': produto,
            'diretorias_regionais': get_diretorias_regionais(lotes),
            'logs': formata_logs(logs)
        }
    )
    return html_to_pdf_response(html_string, f'produto_homologacao_{produto.id_externo}.pdf')


def relatorio_produtos_suspensos(request, payload):
    dado = {
        'homologacoes': payload.get('response', ''),
        'eh_relatorio_por_data': payload.get('eh_por_data', False)
    }
    len_produtos = len(dado['homologacoes'])
    dado['len_produtos'] = len_produtos
    if dado['eh_relatorio_por_data']:
        dado['data_inicio'] = payload.get('data_inicio', '')
        dado['data_fim'] = payload.get('data_fim', '')
    html_string = render_to_string(
        'relatorio_suspensoes_produto.html',
        dado
    )
    return html_to_pdf_response(html_string, 'relatorio_suspensoes_produto.pdf')


def relatorio_produtos_em_analise_sensorial(request, payload):
    data_incial_analise_padrao = payload['produtos'][0]['ultima_homologacao']['log_solicitacao_analise']['criado_em']
    contatos_terceirizada = payload['produtos'][0]['ultima_homologacao']['rastro_terceirizada']['contatos']
    config = get_config_cabecario_relatorio_analise(
        payload['filtros'],
        data_incial_analise_padrao,
        contatos_terceirizada)
    html_string = render_to_string(
        'relatorio_produto_em_analise_sensorial.html',
        {
            'produtos': payload['produtos'],
            'config': config
        }
    )
    return html_to_pdf_response(html_string, 'relatorio_produtos_em_analise_sensorial.pdf')


def relatorio_reclamacao(request, payload):
    html_string = render_to_string(
        'relatorio_reclamacao.html',
        {
            'produtos': payload['produtos'],
            'config': payload['config_cabecario']
        }
    )
    return html_to_pdf_response(html_string, 'relatorio_reclamacao.pdf')


def relatorio_quantitativo_por_terceirizada(request, filtros, dados_relatorio):
    dados_relatorio_transformados = transforma_dados_relatorio_quantitativo(dados_relatorio)
    html_string = render_to_string(
        'relatorio_quantitativo_por_terceirizada.html',
        {
            'filtros': filtros,
            'dados_relatorio': dados_relatorio_transformados,
            'qtde_filtros': conta_filtros(filtros)
        }
    )
    return html_to_pdf_response(html_string, 'relatorio_quantitativo_por_terceirizada.pdf')


def relatorio_produto_analise_sensorial(request, produto):
    homologacao = produto.homologacoes.first()
    terceirizada = homologacao.rastro_terceirizada
    logs = homologacao.logs
    lotes = terceirizada.lotes.all()
    html_string = render_to_string(
        'homologacao_analise_sensorial.html',
        {
            'terceirizada': terceirizada,
            'homologacao': homologacao,
            'fluxo': constants.FLUXO_HOMOLOGACAO_PRODUTO,
            'width': get_width(constants.FLUXO_HOMOLOGACAO_PRODUTO, logs),
            'produto': produto,
            'diretorias_regionais': get_diretorias_regionais(lotes),
            'logs': formata_logs(logs),
            'ultimo_log': homologacao.logs.last()
        }
    )
    return html_to_pdf_response(html_string, f'produto_homologacao_relatorio_{produto.id_externo}.pdf')


def relatorio_produtos_agrupado_terceirizada(request, dados_agrupados, filtros):
    html_string = render_to_string(
        'relatorio_produtos_por_terceirizada.html',
        {
            'dados_agrupados': dados_agrupados,
            'filtros': filtros,
            'qtde_filtros': conta_filtros(filtros)
        }
    )
    return html_to_pdf_response(html_string, 'produtos_homologados_por_terceirizada.pdf')


def relatorio_produtos_situacao(request, queryset, filtros):
    html_string = render_to_string(
        'relatorio_produtos_situacao.html',
        {
            'queryset': queryset,
            'filtros': filtros,
            'qtde_filtros': conta_filtros(filtros)
        }
    )
    return html_to_pdf_response(html_string, 'produtos_situacao.pdf')


def relatorio_produto_analise_sensorial_recebimento(request, produto):
    homologacao = produto.homologacoes.first()
    terceirizada = homologacao.rastro_terceirizada
    logs = homologacao.logs
    lotes = terceirizada.lotes.all()
    html_string = render_to_string(
        'homologacao_analise_sensorial_recebimento.html',
        {
            'terceirizada': terceirizada,
            'homologacao': homologacao,
            'fluxo': constants.FLUXO_HOMOLOGACAO_PRODUTO,
            'width': get_width(constants.FLUXO_HOMOLOGACAO_PRODUTO, logs),
            'produto': produto,
            'diretorias_regionais': get_diretorias_regionais(lotes),
            'logs': formata_logs(logs),
            'ultimo_log': homologacao.logs.last()
        }
    )
    return html_to_pdf_response(html_string, f'produto_homologacao_{produto.id_externo}.pdf')
