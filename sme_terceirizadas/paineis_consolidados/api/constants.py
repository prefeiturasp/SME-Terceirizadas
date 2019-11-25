from ...dados_comuns.constants import DAQUI_A_SETE_DIAS, DAQUI_A_TRINTA_DIAS, SEM_FILTRO

PENDENTES_CIENCIA = 'pendentes-ciencia'
PENDENTES_AUTORIZACAO = 'pendentes-autorizacao'
PENDENTES_VALIDACAO_DRE = 'pendentes-validacao'
AUTORIZADOS = 'autorizados'
_NEGADOS = 'cancelados'
NEGADOS = 'negados'
CANCELADOS = 'cancelados'
PESQUISA = 'pesquisa'

FILTRO_ESCOLA_UUID = '(?P<escola_uuid>[^/.]+)'
FILTRO_DRE_UUID = '(?P<dre_uuid>[^/.]+)'
FILTRO_TERCEIRIZADA_UUID = '(?P<terceirizada_uuid>[^/.]+)'

FILTRO_PERIOD_UUID_DRE = f'(?P<dre_uuid>[^/.]+)/(?P<filtro_aplicado>({SEM_FILTRO}|{DAQUI_A_SETE_DIAS}|{DAQUI_A_TRINTA_DIAS})+)'  # noqa E501

TIPO_VISAO_DRE = 'dre'
TIPO_VISAO_LOTE = 'lote'
TIPO_VISAO_SOLICITACOES = 'tipo_solicitacao'

TIPO_VISAO = f'(?P<tipo_visao>({TIPO_VISAO_DRE}|{TIPO_VISAO_LOTE}|{TIPO_VISAO_SOLICITACOES})+)'
