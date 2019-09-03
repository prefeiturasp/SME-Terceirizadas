MINIMO_DIAS_PARA_PEDIDO = 2
QUANTIDADE_DIAS_OK_PARA_PEDIDO = 5

#
# PEDIDOS
#
SEM_FILTRO = 'sem_filtro'
DAQUI_A_7_DIAS = 'daqui_a_7_dias'
DAQUI_A_30_DIAS = 'daqui_a_30_dias'

PEDIDOS_CODAE = 'pedidos-codae'
PEDIDOS_TERCEIRIZADA = 'pedidos-codae'
PEDIDOS_DRE = 'pedidos-diretoria-regional'
FILTRO_PADRAO_PEDIDOS = f'(?P<filtro_aplicado>({SEM_FILTRO}|{DAQUI_A_7_DIAS}|{DAQUI_A_30_DIAS})+)'

#
# FLUXO
#

SOLICITACOES_DO_USUARIO = 'minhas-solicitacoes'
