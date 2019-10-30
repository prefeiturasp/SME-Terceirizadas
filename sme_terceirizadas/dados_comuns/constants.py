import environ
from .utils import obter_dias_uteis_apos_hoje

env = environ.Env()

DJANGO_EOL_API_TOKEN = env('DJANGO_EOL_API_TOKEN')
DJANGO_EOL_API_URL = env('DJANGO_EOL_API_URL')

PRIORITARIO = 2
LIMITE_INFERIOR = 3
LIMITE_SUPERIOR = 5
REGULAR = 6

MINIMO_DIAS_PARA_PEDIDO = obter_dias_uteis_apos_hoje(PRIORITARIO)
DIAS_UTEIS_LIMITE_INFERIOR = obter_dias_uteis_apos_hoje(LIMITE_INFERIOR)
DIAS_UTEIS_LIMITE_SUPERIOR = obter_dias_uteis_apos_hoje(LIMITE_SUPERIOR)
DIAS_DE_PRAZO_REGULAR_EM_DIANTE = obter_dias_uteis_apos_hoje(REGULAR)

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
# FLUXO, usados nas actions de transição de status nas viewsets dos pedidos/informações do sistema
#

ESCOLA_INICIO_PEDIDO = 'inicio-pedido'
ESCOLA_REVISA_PEDIDO = 'escola-revisa-pedido'
ESCOLA_CANCELA = 'escola-cancela-pedido-48h-antes'
ESCOLA_INFORMA_SUSPENSAO = 'informa-suspensao'

DRE_INICIO_PEDIDO = 'inicio-pedido'
DRE_VALIDA_PEDIDO = 'diretoria-regional-valida-pedido'
DRE_NAO_VALIDA_PEDIDO = 'diretoria-regional-nao-valida-pedido'
DRE_PEDE_REVISAO = 'diretoria-regional-pede-revisao'
DRE_REVISA_PEDIDO = 'diretoria-regional-revisa'
DRE_CANCELA = 'diretoria-regional-cancela'

CODAE_AUTORIZA_PEDIDO = 'codae-autoriza-pedido'
CODAE_NEGA_PEDIDO = 'codae-cancela-pedido'
CODAE_PEDE_REVISAO = 'codae-pediu-revisao'

TERCEIRIZADA_TOMOU_CIENCIA = 'terceirizada-toma-ciencia'

#
# FILTROS
#

SOLICITACOES_DO_USUARIO = 'minhas-solicitacoes'


#
# PERFIS
#

DIRETOR = 'DIRETOR'
