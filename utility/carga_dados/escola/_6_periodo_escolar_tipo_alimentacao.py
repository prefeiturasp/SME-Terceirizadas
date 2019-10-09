from sme_terceirizadas.cardapio.models import TipoAlimentacao
from sme_terceirizadas.escola.models import PeriodoEscolar


def vincula_tipo_alimentcao():
    tipos_alimentacao = TipoAlimentacao.objects.all()
    for periodo in PeriodoEscolar.objects.all():
        periodo.tipos_alimentacao.set(tipos_alimentacao)


print('Run script _6_periodo_escolar_tipo_alimentacao.py')
vincula_tipo_alimentcao()
