from sme_terceirizadas.cardapio.data.motivos_alteracao_cardapio import data_motivoalteracaocardapio
from sme_terceirizadas.cardapio.data.motivos_suspensao_alimentacao import data_motivosuspensao
from sme_terceirizadas.cardapio.data.tipo_alimentacao import data_tipo_alimentacao
from sme_terceirizadas.cardapio.models import MotivoAlteracaoCardapio
from sme_terceirizadas.cardapio.models import MotivoSuspensao
from sme_terceirizadas.cardapio.models import TipoAlimentacao
from utility.carga_dados.helper import ja_existe
from utility.carga_dados.helper import progressbar


def cria_motivoalteracaocardapio():
    for item in progressbar(data_motivoalteracaocardapio, 'Motivo Alteracao Cardapio'):
        _, created = MotivoAlteracaoCardapio.objects.get_or_create(nome=item)
        if not created:
            ja_existe('MotivoAlteracaoCardapio', item)


def cria_motivosuspensao():
    for item in progressbar(data_motivosuspensao, 'Motivo Suspensao'):
        _, created = MotivoSuspensao.objects.get_or_create(nome=item)
        if not created:
            ja_existe('MotivoSuspensao', item)


def cria_tipo_alimentacao():
    for item in progressbar(data_tipo_alimentacao, 'Tipo Alimentacao'):
        _, created = TipoAlimentacao.objects.get_or_create(nome=item)
        if not created:
            ja_existe('TipoAlimentacao', item)
