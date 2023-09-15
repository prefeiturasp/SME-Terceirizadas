import math
import re

from django import template

from ...dados_comuns import constants
from ...dados_comuns.fluxo_status import DietaEspecialWorkflow
from ...dados_comuns.models import LogSolicitacoesUsuario
from ...inclusao_alimentacao.models import (
    GrupoInclusaoAlimentacaoNormal,
    InclusaoAlimentacaoContinua,
    InclusaoAlimentacaoDaCEI,
    InclusaoDeAlimentacaoCEMEI
)

register = template.Library()


@register.filter
def get_attribute(elemento, atributo):
    return getattr(elemento, atributo, False)


@register.filter
def get_element_by_index(indexable, i):
    return indexable[i]


@register.filter
def index_exists(indexable, i):
    return i <= len(indexable)


@register.filter
def check_importada(atributo):
    if (atributo):
        return not atributo
    return True


@register.filter
def fim_de_fluxo(logs):
    fim = False
    for log in logs:
        if ('neg' in log.status_evento_explicacao or 'não' in log.status_evento_explicacao or
            'cancel' in log.status_evento_explicacao):  # noqa
            fim = True
    return fim


@register.filter  # noqa C901
def class_css(log):
    classe_css = 'pending'
    if log.status_evento_explicacao in ['Solicitação Realizada', 'Escola revisou', 'DRE validou', 'DRE revisou',
                                        'CODAE autorizou', 'Terceirizada tomou ciência',
                                        'Escola solicitou cancelamento', 'CODAE autorizou cancelamento',
                                        'Terceirizada tomou ciência do cancelamento',
                                        'CODAE homologou', 'CODAE autorizou reclamação']:
        classe_css = 'active'
    elif log.status_evento_explicacao in ['Escola cancelou', 'DRE cancelou', 'Terceirizada cancelou homologação',
                                          'CODAE suspendeu o produto']:
        classe_css = 'cancelled'
    elif log.status_evento_explicacao in ['DRE não validou', 'CODAE negou', 'Terceirizada recusou',
                                          'CODAE negou cancelamento', 'CODAE não homologou']:
        classe_css = 'disapproved'
    elif log.status_evento_explicacao in ['Questionamento pela CODAE', 'CODAE pediu correção',
                                          'CODAE pediu análise sensorial', 'Escola/Nutricionista reclamou do produto',
                                          'CODAE pediu análise da reclamação', 'Terceirizada respondeu questionamento']:
        classe_css = 'questioned'
    return classe_css


@register.filter
def or_logs(fluxo, logs):
    return logs if len(logs) > len(fluxo) else fluxo


@register.filter
def observacao_padrao(observacao, palavra='...'):
    return observacao or f'Sem observações por parte da {palavra}'


@register.filter
def aceita_nao_aceita_str(aceitou):
    if aceitou:
        return 'Aceitou'
    return 'Não aceitou'


@register.filter
def tem_questionamentos(logs):
    return logs.filter(status_evento=LogSolicitacoesUsuario.CODAE_QUESTIONOU).exists()


@register.filter
def tem_cancelamento(logs):
    return logs.filter(status_evento__in=[LogSolicitacoesUsuario.ESCOLA_CANCELOU,
                                          LogSolicitacoesUsuario.DRE_NAO_VALIDOU,
                                          LogSolicitacoesUsuario.CODAE_NEGOU,
                                          LogSolicitacoesUsuario.DRE_CANCELOU]).exists()


@register.filter
def tem_cancelamento_parcial(dias):
    return dias.filter(cancelado=True).exists()


@register.filter
def concatena_str(query_set):
    return ', '.join([p.nome for p in query_set])


@register.filter
def concatena_string(lista):
    return ', '.join([p for p in lista])


@register.filter
def concatena_label(query_set):
    label = ''
    for item in query_set:
        label += ' e '.join([item.nome])
        if item != list(query_set)[-1]:
            label += ', '
    return label


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def get_total(dictionary):
    return dictionary.get('total')


@register.filter
def get_dado_mes(dictionary, index):
    return dictionary.get('quantidades')[index]


@register.filter
def numero_pra_mes(indice):
    return {
        0: 'Janeiro',
        1: 'Fevereiro',
        2: 'Março',
        3: 'Abril',
        4: 'Maio',
        5: 'Junho',
        6: 'Julho',
        7: 'Agosto',
        8: 'Setembro',
        9: 'Outubro',
        10: 'Novembro',
        11: 'Dezembro',
    }[indice]


@register.filter
def retira_p_texto(texto):
    texto_sem_primeira_tag = texto[3:]
    texto_sem_tag = texto_sem_primeira_tag[:-5]
    return texto_sem_tag


@register.filter
def formata_data(data):
    return data[:10]


@register.filter
def formata_hora(data):
    return data[10:]


@register.filter
def formata_telefone(telefone):
    ddd = telefone[:2]
    numero = telefone[2:]
    return '(' + ddd + ')' + ' ' + numero


@register.filter
def retorna_data_do_ultimo_log(logs):
    return logs[-1]['criado_em'][:10]


@register.filter
def retorna_nome_ultimo_log(logs):
    return logs[-1]['usuario']['nome']


@register.filter
def retorna_rf_ultimo_log(logs):
    return logs[-1]['usuario']['registro_funcional']


@register.filter
def retorna_cargo_ultimo_log(logs):
    return logs[-1]['usuario']['cargo']


@register.filter
def retorna_justificativa_ultimo_log(logs):
    justificativa = logs[-1]['justificativa']
    texto_sem_primeira_tag = justificativa[3:]
    texto_sem_tag = texto_sem_primeira_tag[:-5]
    return texto_sem_tag


@register.filter
def retorn_se_tem_anexo(imagens):
    if len(imagens) > 0:
        return 'Sim'
    return 'Não'


@register.filter
def verifica_se_tem_anexos(logs):
    if len(logs[-1]['anexos']) > 0:
        return 'Sim'
    return 'Não'


@register.filter
def obter_titulo_log_reclamacao(status_evento):
    titulo_log = {
        constants.TERCEIRIZADA_RESPONDEU_RECLAMACAO: 'Resposta terceirizada',
        constants.CODAE_QUESTIONOU_TERCEIRIZADA: 'Questionamento CODAE',
        constants.CODAE_AUTORIZOU_RECLAMACAO: 'Justificativa avaliação CODAE',
        constants.CODAE_RECUSOU_RECLAMACAO: 'Justificativa avaliação CODAE',
        constants.CODAE_RESPONDEU_RECLAMACAO: 'Resposta CODAE'
    }
    return titulo_log.get(status_evento, 'Justificativa')


@register.filter
def obter_rotulo_data_log(status_evento):
    rotulo_data_log = {
        constants.TERCEIRIZADA_RESPONDEU_RECLAMACAO: 'Data resposta terc.',
        constants.CODAE_QUESTIONOU_TERCEIRIZADA: 'Data quest. CODAE',
        constants.CODAE_AUTORIZOU_RECLAMACAO: 'Data avaliação CODAE',
        constants.CODAE_RECUSOU_RECLAMACAO: 'Data avaliação CODAE',
        constants.CODAE_RESPONDEU_RECLAMACAO: 'Data resposta CODAE'
    }
    return rotulo_data_log.get(status_evento, 'Data reclamação')


@register.filter
def obter_titulo_status_dieta(status):
    titulo_status_dieta = {
        DietaEspecialWorkflow.CODAE_A_AUTORIZAR: 'Aguardando Autorização',
        DietaEspecialWorkflow.CODAE_AUTORIZADO: 'Autorizada',
        DietaEspecialWorkflow.CODAE_NEGOU_PEDIDO: 'Negada',
        DietaEspecialWorkflow.ESCOLA_CANCELOU: 'Cancelada'
    }
    return titulo_status_dieta.get(status, '')


@register.filter
def retorna_lote(valor):
    if 'LOTE' in valor:
        return valor[5:]
    return valor


@register.simple_tag
def embalagens_filter(embalagens, tipo):
    for emb in embalagens:
        if emb.tipo_embalagem == tipo:
            return emb
    else:
        return False


@register.simple_tag
def get_assinatura_cronograma(logs):
    return logs.filter(status_evento=LogSolicitacoesUsuario.CRONOGRAMA_ENVIADO_AO_FORNECEDOR).last()


@register.simple_tag
def get_assinatura_fornecedor(logs):
    return logs.filter(status_evento=LogSolicitacoesUsuario.CRONOGRAMA_ASSINADO_PELO_FORNECEDOR).last()


@register.simple_tag
def get_assinatura_dinutre(logs):
    return logs.filter(status_evento=LogSolicitacoesUsuario.CRONOGRAMA_ASSINADO_PELA_DINUTRE).last()


@register.simple_tag
def get_assinatura_codae(logs):
    return logs.filter(status_evento=LogSolicitacoesUsuario.CRONOGRAMA_ASSINADO_PELA_CODAE).last()


@register.filter
def existe_inclusao_cancelada(solicitacao):
    status_ = solicitacao['status'] if isinstance(solicitacao, dict) else solicitacao.status
    inclusoes_ = solicitacao['datas_intervalo'] if isinstance(solicitacao, dict) else solicitacao.inclusoes
    return (status_ == 'ESCOLA_CANCELOU' or
            inclusoes_.filter(cancelado_justificativa__isnull=False).exclude(cancelado_justificativa='').exists())


@register.filter
def eh_inclusao(solicitacao):
    return (
        isinstance(solicitacao, GrupoInclusaoAlimentacaoNormal) or
        isinstance(solicitacao, InclusaoAlimentacaoContinua) or
        isinstance(solicitacao, InclusaoAlimentacaoDaCEI) or
        isinstance(solicitacao, InclusaoDeAlimentacaoCEMEI)
    )


@register.filter
def formatar_cpf(cpf):
    try:
        inicio = cpf[:2]
        fim = cpf[-2:]
        return inicio + '*.***.***-' + fim
    except Exception:
        return cpf


@register.filter
def inclusao_multiplos_cancelamentos(solicitacao):
    multiplos_cancelamentos = len(set(list(solicitacao.inclusoes.filter(
        cancelado_justificativa__isnull=False).values_list(
        'cancelado_justificativa', flat=True)))) > 1
    return multiplos_cancelamentos


@register.filter
def inclusoes_canceladas(solicitacao):
    if solicitacao.status == 'ESCOLA_CANCELOU':
        return solicitacao.inclusoes.all()
    return solicitacao.inclusoes.filter(cancelado_justificativa__isnull=False).exclude(cancelado_justificativa='')


@register.filter
def formatar_data_solicitacoes_alimentacao(data):
    try:
        return data.strftime('%d/%m/%Y')
    except Exception:
        return data


@register.simple_tag
def get_valor_somatorio_campo_periodo(tabela_somatorio, campo, periodo):
    for item in tabela_somatorio:
        if item['campo'] == campo and item['periodo'] == periodo:
            return item['valor']
    return '-'


@register.simple_tag
def total_periodo_ou_campo_medicao(tabela_somatorio, periodo_ou_campo):
    total = 0
    for item in tabela_somatorio:
        if item['periodo'] == periodo_ou_campo or item['campo'] == periodo_ou_campo:
            total += item['valor']
    return total


@register.filter
def get_total_medicao(tabela_somatorio):
    total = 0
    for item in tabela_somatorio:
        total += item['valor']
    return total


@register.filter
def get_matriculados(uuid, alunos_matriculados):
    periodo = alunos_matriculados['periodo_escolar']
    alunos_no_periodo = alunos_matriculados['alunos_por_faixa_etaria'][periodo]
    if alunos_no_periodo and alunos_no_periodo[uuid]:
        return alunos_matriculados['alunos_por_faixa_etaria'][periodo][uuid]
    else:
        return 0


@register.filter
def get_nao_eh_dia_letivo(dias_letivos, i):
    try:
        return not dias_letivos[i]
    except IndexError:
        return False
    except Exception as e:
        return False


@register.filter
def get_nome_campo(campo):
    campos = {
        'numero_de_alunos': 'Número de Alunos',
        'matriculados': 'Matriculados',
        'aprovadas': 'Aprovadas',
        'frequencia': 'Frequência',
        'solicitado': 'Solicitado',
        'consumido': 'Consumido',
        'desjejum': 'Desjejum',
        'lanche': 'Lanche',
        'lanche_4h': 'Lanche 4h',
        'refeicao': 'Refeição 1 Oferta',
        'repeticao_refeicao': 'Repetição de Refeição',
        'lanche_emergencial': 'Lanche Emergencial',
        'kit_lanche': 'Kit Lanche',
        'total_refeicoes_pagamento': 'Total de Refeições para Pagamento',
        'sobremesa': 'Sobremesa 1 Oferta',
        'repeticao_sobremesa': 'Repetição de Sobremesa',
        'total_sobremesas_pagamento': 'Total de Sobremesas para Pagamento'
    }
    return campos.get(campo, campo)


def get_dias(observacoes_tuple):
    dias = []
    for obs in observacoes_tuple:
        if obs[0] not in dias:
            dias.append(obs[0])
    return dias


@register.filter
def formatar_observacoes(observacoes):
    MAX_LINHAS_POR_PAGINA = 22
    observacoes_tuple = []
    for observacao in observacoes:
        obs_list = list(observacao)
        if obs_list[4] and obs_list[1]:
            obs_list[4] = f'{obs_list[4]} - ' + f'{obs_list[1]}'
        elif obs_list[4] and not obs_list[1]:
            obs_list[4] = obs_list[4]
        else:
            obs_list[4] = obs_list[1]
        obs_list[3] = re.sub(r'<.*?>', '', obs_list[3])
        observacoes_tuple.append(tuple(obs_list))
    observacoes_ordenadas_corretamente = []
    dias = get_dias(observacoes_tuple)
    for dia in dias:
        obs_filtradas_por_dia = tuple(filter(lambda obs: obs[0] == dia, observacoes_tuple))
        obs_ordenadas_periodo_grupo = sorted(obs_filtradas_por_dia, key=lambda k: constants.ORDEM_PERIODOS_GRUPOS[k[4]])
        [observacoes_ordenadas_corretamente.append(i) for i in obs_ordenadas_periodo_grupo]
    tabelas_observacoes = []
    i = 1
    while i <= math.ceil(len(observacoes_ordenadas_corretamente) / MAX_LINHAS_POR_PAGINA):
        tabelas_observacoes.append(
            observacoes_ordenadas_corretamente[(MAX_LINHAS_POR_PAGINA * (i - 1)):(MAX_LINHAS_POR_PAGINA * i)]
        )
        i += 1

    return tabelas_observacoes
