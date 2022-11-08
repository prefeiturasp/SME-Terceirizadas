from django import template

from ...dados_comuns import constants
from ...dados_comuns.fluxo_status import DietaEspecialWorkflow
from ...dados_comuns.models import LogSolicitacoesUsuario

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
                                          'CODAE pediu análise da reclamação']:
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


@register.filter
def existe_inclusao_cancelada(solicitacao):
    return solicitacao.inclusoes.filter(cancelado=True).exists()


@register.filter
def inclusoes_canceladas(solicitacao):
    return solicitacao.inclusoes.filter(cancelado=True)
