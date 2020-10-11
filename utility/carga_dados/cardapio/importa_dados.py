from random import randint, sample
from utility.carga_dados.helper import ja_existe, progressbar

from sme_terceirizadas.cardapio.data.motivos_alteracao_cardapio import data_motivoalteracaocardapio
from sme_terceirizadas.cardapio.data.motivos_suspensao_alimentacao import data_motivosuspensao
from sme_terceirizadas.cardapio.data.tipo_alimentacao import data_tipo_alimentacao
from sme_terceirizadas.cardapio.models import (
    ComboDoVinculoTipoAlimentacaoPeriodoTipoUE,
    MotivoAlteracaoCardapio,
    MotivoSuspensao,
    TipoAlimentacao,
    VinculoTipoAlimentacaoComPeriodoEscolarETipoUnidadeEscolar,
)
from sme_terceirizadas.escola.models import PeriodoEscolar, TipoUnidadeEscolar


def cria_motivoalteracaocardapio():
    for item in progressbar(data_motivoalteracaocardapio, 'Motivo Alteracao Cardapio'):  # noqa
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


def cria_vinculo_tipo_alimentacao_com_periodo_escolar_e_tipo_unidade_escolar():
    # Percorre todos os tipos de unidade escolar e todos os periodos escolares.
    VinculoTipoAlimentacaoComPeriodoEscolarETipoUnidadeEscolar.objects.all().delete()  # noqa
    tipo_unidade_escolares = TipoUnidadeEscolar.objects.all()
    periodo_escolares = PeriodoEscolar.objects.all()
    aux = []
    for tipo_unidade_escolar in progressbar(tipo_unidade_escolares, 'VinculoTipoAlimentacaoComPeriodoEscolarETipoUnidadeEscolar'):  # noqa
        for periodo_escolar in periodo_escolares:
            obj = VinculoTipoAlimentacaoComPeriodoEscolarETipoUnidadeEscolar(
                tipo_unidade_escolar=tipo_unidade_escolar,
                periodo_escolar=periodo_escolar,
            )
            aux.append(obj)
    VinculoTipoAlimentacaoComPeriodoEscolarETipoUnidadeEscolar.objects.bulk_create(aux)  # noqa


def cria_combo_do_vinculo_tipo_alimentacao_periodo_tipo_ue():
    ComboDoVinculoTipoAlimentacaoPeriodoTipoUE.objects.all().delete()
    vinculos = VinculoTipoAlimentacaoComPeriodoEscolarETipoUnidadeEscolar.objects.all()  # noqa
    tipos_alimentacoes = list(TipoAlimentacao.objects.all())
    for vinculo in progressbar(vinculos, 'ComboDoVinculoTipoAlimentacaoPeriodoTipoUE'):  # noqa
        # Cria vários combos para cada vinculo.
        for _ in range(randint(3, 7)):
            obj = ComboDoVinculoTipoAlimentacaoPeriodoTipoUE.objects.create(vinculo=vinculo)  # noqa
            tipos_amostra = sample(tipos_alimentacoes, 3)
            for item in tipos_amostra:
                obj.tipos_alimentacao.add(item)
