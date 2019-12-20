from ...dados_comuns.constants import DAQUI_A_SETE_DIAS, DAQUI_A_TRINTA_DIAS, SEM_FILTRO

PENDENTES_CIENCIA = 'pendentes-ciencia'
PENDENTES_AUTORIZACAO = 'pendentes-autorizacao'
PENDENTES_VALIDACAO_DRE = 'pendentes-validacao'
AUTORIZADOS = 'autorizados'
QUESTIONAMENTOS = 'questionamentos'
_NEGADOS = 'cancelados'
NEGADOS = 'negados'
CANCELADOS = 'cancelados'
PESQUISA = 'pesquisa'
RESUMO_MES = 'resumo-mes'

FILTRO_ESCOLA_UUID = '(?P<escola_uuid>[^/.]+)'
FILTRO_DRE_UUID = '(?P<dre_uuid>[^/.]+)'
FILTRO_TERCEIRIZADA_UUID = '(?P<terceirizada_uuid>[^/.]+)'

FILTRO_PERIOD_UUID_DRE = f'(?P<dre_uuid>[^/.]+)/(?P<filtro_aplicado>({SEM_FILTRO}|{DAQUI_A_SETE_DIAS}|{DAQUI_A_TRINTA_DIAS})+)'  # noqa E501

TIPO_VISAO_DRE = 'dre'
TIPO_VISAO_LOTE = 'lote'
TIPO_VISAO_SOLICITACOES = 'tipo_solicitacao'

TIPO_VISAO = f'(?P<tipo_visao>({TIPO_VISAO_DRE}|{TIPO_VISAO_LOTE}|{TIPO_VISAO_SOLICITACOES})+)'

FILTRO_DATA_INICIAL = '(?P<filtro_aplicado>(sem_filtro|daqui_a_7_dias|daqui_a_30_dias)+)'
TIPO_SOLICITACAO = '(?P<tipo_solicitacao>(ALT_CARDAPIO|INV_CARDAPIO|INC_ALIMENTA|INC_ALIMENTA_CONTINUA|KIT_LANCHE_AVULSA|SUSP_ALIMENTACAO|KIT_LANCHE_UNIFICADA|TODOS)+)'  # noqa
STATUS_SOLICITACAO = '(?P<status_solicitacao>(AUTORIZADOS|NEGADOS|CANCELADOS|EM_ANDAMENTO|TODOS)+)'
DATA_INICIAL = '(?P<data_inicial>.*)'
DATA_FINAL = '(?P<data_final>.*)'
