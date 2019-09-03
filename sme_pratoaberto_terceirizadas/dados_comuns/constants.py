from .utils import obter_dias_uteis_apos_hoje

MINIMO_DIAS_PARA_PEDIDO = obter_dias_uteis_apos_hoje(2)
DIAS_UTEIS_LIMITE_INFERIOR = obter_dias_uteis_apos_hoje(3)
DIAS_UTEIS_LIMITE_SUPERIOR = obter_dias_uteis_apos_hoje(5)
DIAS_DE_PRAZO_REGULAR_EM_DIANTE = obter_dias_uteis_apos_hoje(6)

#
# PEDIDOS
#

SEM_FILTRO = 'sem_filtro'
DAQUI_A_7_DIAS = 'daqui_a_7_dias'
DAQUI_A_30_DIAS = 'daqui_a_30_dias'

PEDIDOS_CODAE = 'pedidos-codae'
PEDIDOS_TERCEIRIZADA = 'pedidos-terceirizadas'
PEDIDOS_DRE = 'pedidos-diretoria-regional'
FILTRO_PADRAO_PEDIDOS = f'(?P<filtro_aplicado>({SEM_FILTRO}|{DAQUI_A_7_DIAS}|{DAQUI_A_30_DIAS})+)'

#
# FLUXO
#

SOLICITACOES_DO_USUARIO = 'minhas-solicitacoes'
