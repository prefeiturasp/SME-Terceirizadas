from sme_pratoaberto_terceirizadas.cardapio.models import TipoAlimentacao
from sme_pratoaberto_terceirizadas.escola.models import PeriodoEscolar


def vincula_tipo_alimentcao():
    tipos_alimentacao = TipoAlimentacao.objects.all()
    for periodo in PeriodoEscolar.objects.all():
        periodo.tipos_alimentacao.set(tipos_alimentacao)


vincula_tipo_alimentcao()
