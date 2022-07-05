import datetime

import environ
from django.contrib.staticfiles.storage import staticfiles_storage
from django.db.models import F, FloatField, Sum
from django.template.loader import get_template, render_to_string

from ..dados_comuns.fluxo_status import GuiaRemessaWorkFlow as GuiaStatus
from ..dados_comuns.fluxo_status import ReclamacaoProdutoWorkflow
from ..dados_comuns.models import LogSolicitacoesUsuario
from ..kit_lanche.models import EscolaQuantidade
from ..logistica.api.helpers import retorna_status_guia_remessa
from ..relatorios.utils import html_to_pdf_cancelada, html_to_pdf_file, html_to_pdf_multiple, html_to_pdf_response
from ..terceirizada.utils import transforma_dados_relatorio_quantitativo
from . import constants
from .utils import (
    conta_filtros,
    formata_logs,
    get_config_cabecario_relatorio_analise,
    get_diretorias_regionais,
    get_ultima_justificativa_analise_sensorial,
    get_width
)

env = environ.Env()


def relatorio_filtro_periodo(request, query_set_consolidado, escola_nome='', dre_nome=''):
    # TODO: se query_set_consolidado tiver muitos resultados, pode demorar no front-end
    # melhor mandar via celery pro email de quem solicitou
    # ou por padrão manda tudo pro celery
    request_params = request.GET

    tipo_solicitacao = request_params.get('tipo_solicitacao', 'INVALIDO')
    status_solicitacao = request_params.get('status_solicitacao', 'INVALIDO')
    data_inicial = datetime.datetime.strptime(
        request_params.get('data_inicial'), '%Y-%m-%d')
    data_final = datetime.datetime.strptime(
        request_params.get('data_final'), '%Y-%m-%d')
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
    qtd_escolas = EscolaQuantidade.objects.filter(
        solicitacao_unificada=solicitacao).count()

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
         'fluxo': constants.FLUXO_ALTERACAO_DE_CARDAPIO,
         'width': get_width(constants.FLUXO_ALTERACAO_DE_CARDAPIO, solicitacao.logs),
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


def relatorio_dieta_especial_conteudo(solicitacao):
    if solicitacao.tipo_solicitacao == 'COMUM':
        escola = solicitacao.rastro_escola
    else:
        escola = solicitacao.escola_destino
    escola_origem = solicitacao.rastro_escola
    logs = solicitacao.logs
    if solicitacao.logs.filter(status_evento=LogSolicitacoesUsuario.INICIO_FLUXO_INATIVACAO).exists():
        if solicitacao.logs.filter(status_evento=LogSolicitacoesUsuario.TERCEIRIZADA_TOMOU_CIENCIA).exists():
            fluxo = constants.FLUXO_DIETA_ESPECIAL_INATIVACAO
        else:
            fluxo = constants.FLUXO_DIETA_ESPECIAL_INATIVACAO_INCOMPLETO
    else:
        fluxo = constants.FLUXO_DIETA_ESPECIAL
    eh_importado = solicitacao.eh_importado
    html_string = render_to_string(
        'solicitacao_dieta_especial.html',
        {
            'escola': escola,
            'escola_origem': escola_origem,
            'lote': escola.lote,
            'solicitacao': solicitacao,
            'fluxo': fluxo,
            'width': get_width(fluxo, solicitacao.logs),
            'logs': formata_logs(logs),
            'eh_importado': eh_importado,
            'foto_aluno': solicitacao.aluno.foto_aluno_base64
        }
    )
    return html_string


def relatorio_guia_de_remessa(guias, is_async=False): # noqa C901
    SERVER_NAME = env.str('SERVER_NAME', default=None)
    page = None
    lista_pdfs = []
    for guia in guias:
        lista_imagens_conferencia = []
        lista_imagens_reposicao = []
        conferencias_individuais = []
        reposicoes_individuais = []
        reposicao = None
        insucesso = guia.insucessos.last() if guia.insucessos else None
        todos_alimentos = guia.alimentos.all().annotate(
            peso_total=Sum(
                F('embalagens__capacidade_embalagem') * F('embalagens__qtd_volume'), output_field=FloatField()
            )
        )

        if guia.status == GuiaStatus.PENDENTE_DE_CONFERENCIA or guia.status == GuiaStatus.CANCELADA:
            conferencia = None
            reposicao = None
        elif guia.status == GuiaStatus.RECEBIDA:
            conferencia = guia.conferencias.last()

        else:
            conferencia = guia.conferencias.filter(eh_reposicao=False).last()
            reposicao = guia.conferencias.filter(eh_reposicao=True).last()
            if conferencia:
                conferencias_individuais = conferencia.conferencia_dos_alimentos.all()
            if reposicao:
                reposicoes_individuais = reposicao.conferencia_dos_alimentos.all()
            for alimento_guia in todos_alimentos:
                conferencias_alimento = []
                reposicoes_alimento = []
                for alimento_conferencia in conferencias_individuais:
                    if alimento_guia.nome_alimento == alimento_conferencia.nome_alimento:
                        for embalagem in alimento_guia.embalagens.all():
                            if embalagem.tipo_embalagem == alimento_conferencia.tipo_embalagem:
                                embalagem.qtd_recebido = alimento_conferencia.qtd_recebido
                                embalagem.ocorrencia = alimento_conferencia.ocorrencia
                                embalagem.observacao = alimento_conferencia.observacao
                                embalagem.arquivo = alimento_conferencia.arquivo
                                if alimento_conferencia.arquivo:
                                    imagem = {
                                        'nome_alimento': alimento_guia.nome_alimento,
                                        'arquivo': alimento_conferencia.arquivo
                                    }
                                    lista_filtrada = [a for a in lista_imagens_conferencia
                                                      if a['nome_alimento'] == alimento_guia.nome_alimento]
                                    if not lista_filtrada:
                                        lista_imagens_conferencia.append(imagem)
                                conferencias_alimento.append(embalagem)
                        alimento_guia.embalagens_conferidas = conferencias_alimento
                for alimento_reposicao in reposicoes_individuais:
                    if alimento_guia.nome_alimento == alimento_reposicao.nome_alimento:
                        for embalagem in alimento_guia.embalagens.all():
                            if embalagem.tipo_embalagem == alimento_reposicao.tipo_embalagem:
                                embalagem.qtd_recebido = alimento_reposicao.qtd_recebido
                                embalagem.ocorrencia = alimento_reposicao.ocorrencia
                                embalagem.observacao = alimento_reposicao.observacao
                                embalagem.arquivo = alimento_reposicao.arquivo
                                if alimento_reposicao.arquivo:
                                    imagem = {
                                        'nome_alimento': alimento_guia.nome_alimento,
                                        'arquivo': alimento_reposicao.arquivo
                                    }
                                    lista_filtrada = [a for a in lista_imagens_reposicao
                                                      if a['nome_alimento'] == alimento_guia.nome_alimento]
                                    if not lista_filtrada:
                                        lista_imagens_reposicao.append(imagem)
                                reposicoes_alimento.append(embalagem)
                        alimento_guia.embalagens_repostas = reposicoes_alimento

        if todos_alimentos:
            page = guia.as_dict()
            peso_total_pagina = round(sum(alimento.peso_total for alimento in todos_alimentos), 2)
            page['alimentos'] = todos_alimentos
            page['peso_total'] = peso_total_pagina
            page['status_guia'] = retorna_status_guia_remessa(page['status'])
            page['insucesso'] = insucesso
            page['conferencia'] = conferencia
            page['reposicao'] = reposicao
            page['lista_imagens_conferencia'] = lista_imagens_conferencia
            page['lista_imagens_reposicao'] = lista_imagens_reposicao

        html_template = get_template('logistica/guia_remessa/relatorio_guia.html')
        html_string = html_template.render({'pages': [page], 'URL': SERVER_NAME,
                                            'base_static_url': staticfiles_storage.location})

        data_arquivo = datetime.datetime.today().strftime('%d/%m/%Y às %H:%M')

        lista_pdfs.append(html_string.replace('dt_file', data_arquivo))

    if len(lista_pdfs) == 1:
        if guia.status == GuiaStatus.CANCELADA:
            return html_to_pdf_cancelada(lista_pdfs[0], f'guia_{guia.numero_guia}.pdf', is_async)
        else:
            return html_to_pdf_file(lista_pdfs[0], f'guia_{guia.numero_guia}.pdf', is_async)
    else:
        return html_to_pdf_multiple(lista_pdfs, 'guias_de_remessa.pdf', is_async)


def relatorio_dieta_especial(request, solicitacao):
    html_string = relatorio_dieta_especial_conteudo(solicitacao)
    return html_to_pdf_response(html_string, f'dieta_especial_{solicitacao.id_externo}.pdf')


def relatorio_dietas_especiais_terceirizada(request, dados):
    html_string = render_to_string('relatorio_dietas_especiais_terceirizada.html', dados)
    return html_to_pdf_response(html_string, f'dietas_especiais.pdf')


def relatorio_dieta_especial_protocolo(request, solicitacao):
    if solicitacao.tipo_solicitacao == 'COMUM':
        escola = solicitacao.rastro_escola
    else:
        escola = solicitacao.escola_destino
    substituicao_ordenada = solicitacao.substituicoes.order_by('alimento__nome')
    html_string = render_to_string(
        'solicitacao_dieta_especial_protocolo.html',
        {
            'escola': escola,
            'solicitacao': solicitacao,
            'substituicoes': substituicao_ordenada,
            'data_termino': solicitacao.data_termino,
            'log_autorizacao': solicitacao.logs.get(status_evento=LogSolicitacoesUsuario.CODAE_AUTORIZOU),
            'foto_aluno': solicitacao.aluno.foto_aluno_base64
        }
    )
    if request:
        return html_to_pdf_response(html_string, f'dieta_especial_{solicitacao.id_externo}.pdf')
    else:
        return html_string


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
            'escola': escola, 'solicitacao': solicitacao,
            'fluxo': constants.FLUXO_INCLUSAO_ALIMENTACAO,
            'width': get_width(constants.FLUXO_INCLUSAO_ALIMENTACAO, solicitacao.logs),
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
    TEMPO_PASSEIO = {
        '0': 'até 4 horas',
        '1': 'de 5 a 7 horas',
        '2': '8 horas ou mais'
    }
    escola = solicitacao.rastro_escola
    logs = solicitacao.logs
    observacao = solicitacao.solicitacao_kit_lanche.descricao
    solicitacao.observacao = observacao
    tempo_passeio_num = str(solicitacao.solicitacao_kit_lanche.tempo_passeio)
    tempo_passeio = TEMPO_PASSEIO.get(tempo_passeio_num)
    html_string = render_to_string(
        'solicitacao_kit_lanche_passeio.html',
        {
            'tempo_passeio': tempo_passeio,
            'escola': escola,
            'solicitacao': solicitacao,
            'quantidade_kits': solicitacao.solicitacao_kit_lanche.kits.all().count() * solicitacao.quantidade_alunos,
            'fluxo': constants.FLUXO_KIT_LANCHE_PASSEIO,
            'width': get_width(constants.FLUXO_KIT_LANCHE_PASSEIO, solicitacao.logs),
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
    data_de = solicitacao.cardapio_de.data if solicitacao.cardapio_de else solicitacao.data_de_inversao
    data_para = solicitacao.cardapio_para.data if solicitacao.cardapio_para else solicitacao.data_para_inversao
    html_string = render_to_string(
        'solicitacao_inversao_de_cardapio.html',
        {
            'escola': escola,
            'solicitacao': solicitacao,
            'data_de': data_de,
            'data_para': data_para,
            'fluxo': constants.FLUXO_INVERSAO_DIA_CARDAPIO,
            'width': get_width(constants.FLUXO_INVERSAO_DIA_CARDAPIO, solicitacao.logs),
            'logs': formata_logs(logs)
        }
    )
    return html_to_pdf_response(html_string, f'solicitacao_inversao_{solicitacao.id_externo}.pdf')


def relatorio_suspensao_de_alimentacao(request, solicitacao):
    escola = solicitacao.rastro_escola
    logs = solicitacao.logs
    # TODO: GrupoSuspensaoAlimentacaoSerializerViewSet não tem motivo, quem
    # tem é cada suspensão do relacionamento
    suspensoes = solicitacao.suspensoes_alimentacao.all()
    quantidades_por_periodo = solicitacao.quantidades_por_periodo.all()
    html_string = render_to_string(
        'solicitacao_suspensao_de_alimentacao.html',
        {
            'escola': escola,
            'solicitacao': solicitacao,
            'suspensoes': suspensoes,
            'quantidades_por_periodo': quantidades_por_periodo,
            'fluxo': constants.FLUXO_SUSPENSAO_ALIMENTACAO,
            'width': get_width(constants.FLUXO_SUSPENSAO_ALIMENTACAO, solicitacao.logs),
            'logs': formata_logs(logs)
        }
    )
    return html_to_pdf_response(html_string, f'solicitacao_suspensao_{solicitacao.id_externo}.pdf')


def relatorio_produto_homologacao(request, produto):
    homologacao = produto.homologacao
    terceirizada = homologacao.rastro_terceirizada
    reclamacao = homologacao.reclamacoes.filter(
        status=ReclamacaoProdutoWorkflow.CODAE_ACEITOU).first()
    logs = homologacao.logs
    lotes = terceirizada.lotes.all()
    justificativa_analise_sensorial = get_ultima_justificativa_analise_sensorial(produto)
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
            'logs': formata_logs(logs),
            'justificativa_analise_sensorial': justificativa_analise_sensorial
        }
    )
    return html_to_pdf_response(html_string, f'produto_homologacao_{produto.id_externo}.pdf')


def relatorio_marcas_por_produto_homologacao(request, produtos, filtros):
    html_string = render_to_string(
        'homologacao_marcas_por_produto.html',
        {
            'produtos': produtos,
            'hoje': datetime.date.today(),
            'filtros': filtros
        }
    )
    return html_to_pdf_response(html_string, f'relatorio_marcas_por_produto_homologacao.pdf')


def relatorio_produtos_suspensos(produtos, filtros):
    if filtros['cabecario_tipo'] == 'CABECARIO_POR_DATA' and 'data_suspensao_inicial' not in filtros:
        data_suspensao_inicial = datetime.datetime.today()
        for produto in produtos:
            ultimo_log = produto.ultima_homologacao.ultimo_log
            if ultimo_log.criado_em < data_suspensao_inicial:
                data_suspensao_inicial = ultimo_log.criado_em
        filtros['data_suspensao_inicial'] = data_suspensao_inicial.strftime(
            '%d/%m/%Y')

    html_string = render_to_string(
        'relatorio_suspensoes_produto.html',
        {
            'produtos': produtos,
            'config': filtros
        }
    )
    return html_to_pdf_response(html_string, 'relatorio_suspensoes_produto.pdf')


def relatorio_produtos_em_analise_sensorial(produtos, filtros):
    data_incial_analise_padrao = produtos[0]['ultima_homologacao'][
        'log_solicitacao_analise']['criado_em']
    contatos_terceirizada = produtos[0]['ultima_homologacao'][
        'rastro_terceirizada']['contatos']
    config = get_config_cabecario_relatorio_analise(
        filtros,
        data_incial_analise_padrao,
        contatos_terceirizada)
    html_string = render_to_string(
        'relatorio_produto_em_analise_sensorial.html',
        {
            'produtos': produtos,
            'config': config
        }
    )
    return html_to_pdf_response(html_string, 'relatorio_produtos_em_analise_sensorial.pdf')


def relatorio_reclamacao(produtos, filtros):
    if filtros['cabecario_tipo'] == 'CABECARIO_POR_DATA' and 'data_inicial_reclamacao' not in filtros:
        data_inicial_reclamacao = datetime.datetime.today()
        for produto in produtos:
            reclamacao = produto.ultima_homologacao.reclamacoes.first()
            if reclamacao.criado_em < data_inicial_reclamacao:
                data_inicial_reclamacao = reclamacao.criado_em
        filtros['data_inicial_reclamacao'] = data_inicial_reclamacao.strftime(
            '%d/%m/%Y')
    html_string = render_to_string(
        'relatorio_reclamacao.html',
        {
            'produtos': produtos,
            'config': filtros
        }
    )
    return html_to_pdf_response(html_string, 'relatorio_reclamacao.pdf')


def relatorio_quantitativo_por_terceirizada(request, filtros, dados_relatorio):
    dados_relatorio_transformados = transforma_dados_relatorio_quantitativo(
        dados_relatorio)
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
    homologacao = produto.homologacao
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
    homologacao = produto.homologacao
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


def get_relatorio_dieta_especial(campos, form, queryset, user, nome_relatorio):
    status = None
    if 'status' in form.cleaned_data:
        status = dict(form.fields['status'].choices).get(
            form.cleaned_data['status'], '')
    html_string = render_to_string(
        f'{nome_relatorio}.html',
        {
            'campos': campos,
            'status': status,
            'filtros': form.cleaned_data,
            'queryset': queryset,
            'user': user
        }
    )
    return html_to_pdf_response(html_string, f'{nome_relatorio}.pdf')


def relatorio_quantitativo_solic_dieta_especial(campos, form, queryset, user):
    return get_relatorio_dieta_especial(
        campos, form, queryset, user, 'relatorio_quantitativo_solicitacoes_dieta_especial')


def relatorio_quantitativo_classificacao_dieta_especial(campos, form, queryset, user):
    return get_relatorio_dieta_especial(
        campos, form, queryset, user, 'relatorio_quantitativo_classificacao_dieta_especial')


def relatorio_quantitativo_diag_dieta_especial(campos, form, queryset, user):
    return get_relatorio_dieta_especial(
        campos,
        form,
        queryset,
        user,
        'relatorio_quantitativo_diagnostico_dieta_especial'
    )


def relatorio_quantitativo_diag_dieta_especial_somente_dietas_ativas(campos, form, queryset, user):
    return get_relatorio_dieta_especial(
        campos,
        form,
        queryset,
        user,
        'relatorio_quantitativo_diagnostico_dieta_especial_somente_dietas_ativas'
    )


def relatorio_geral_dieta_especial(form, queryset, user):
    return get_relatorio_dieta_especial(
        None, form, queryset, user, 'relatorio_dieta_especial')


def get_pdf_guia_distribuidor(data=None, many=False):
    pages = []
    inicio = 0
    num_alimentos_pagina = 4
    for guia in data:
        todos_alimentos = guia.alimentos.all().annotate(
            peso_total=Sum(
                F('embalagens__capacidade_embalagem') * F('embalagens__qtd_volume'), output_field=FloatField()
            )
        )
        while True:
            alimentos = todos_alimentos[inicio:inicio + num_alimentos_pagina]
            if alimentos:
                page = guia.as_dict()
                peso_total_pagina = round(sum(alimento.peso_total for alimento in alimentos), 2)
                page['alimentos'] = alimentos
                page['peso_total'] = peso_total_pagina
                pages.append(page)
                inicio = inicio + num_alimentos_pagina
            else:
                break
        inicio = 0
    html_string = render_to_string('logistica/guia_distribuidor/guia_distribuidor_v2.html', {'pages': pages})
    data_arquivo = datetime.date.today().strftime('%d/%m/%Y')

    return html_to_pdf_response(html_string.replace('dt_file', data_arquivo), 'guia_de_remessa.pdf')
