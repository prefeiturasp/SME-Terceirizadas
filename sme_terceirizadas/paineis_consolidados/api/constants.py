from ...dados_comuns.constants import DAQUI_A_30_DIAS, DAQUI_A_7_DIAS, SEM_FILTRO

PENDENTES_APROVACAO = 'pendentes-aprovacao'
PENDENTES_VALIDACAO_DRE = 'pendentes-validacao'
AUTORIZADOS = 'aprovados'
_NEGADOS = 'cancelados'
NEGADOS = 'negados'
CANCELADOS = 'cancelados'

FILTRO_ESCOLA_UUID = '(?P<escola_uuid>[^/.]+)'
FILTRO_DRE_UUID = '(?P<dre_uuid>[^/.]+)'
FILTRO_TERCEIRIZADA_UUID = '(?P<terceirizada_uuid>[^/.]+)'

FILTRO_PERIOD_UUID_DRE = f'(?P<dre_uuid>[^/.]+)/(?P<filtro_aplicado>({SEM_FILTRO}|{DAQUI_A_7_DIAS}|{DAQUI_A_30_DIAS})+)'
