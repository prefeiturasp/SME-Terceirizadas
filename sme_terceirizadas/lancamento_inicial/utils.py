from calendar import monthrange
from datetime import date

from django.db.models import Count, F, Q, Sum
from workalendar.america import BrazilSaoPauloCity

from ..dados_comuns.fluxo_status import PedidoAPartirDaEscolaWorkflow
from ..kit_lanche.models import SolicitacaoKitLancheAvulsa
from ..inclusao_alimentacao.models import QuantidadePorPeriodo

def mes_para_faixa(mes_string):
    (mes, ano) = mes_string.split('/')
    mes = int(mes)
    ano = int(ano)
    ultimo_dia_do_mes = monthrange(ano, mes)[1]
    return (
        date(ano, mes, 1),
        date(ano, mes, ultimo_dia_do_mes),
    )


def eh_feriado_ou_fds(data):
    calendario = BrazilSaoPauloCity()
    return data.weekday() >= 5 or calendario.is_holiday(data)


def total_merendas_secas_por_escola_periodo_escolar_e_data(escola_periodo_escolar, data):
    total_merendas_secas = QuantidadePorPeriodo.objects.filter(
        Q(
            inclusao_alimentacao_continua__escola=escola_periodo_escolar.escola,
            inclusao_alimentacao_continua__data_inicial__lte=data,
            inclusao_alimentacao_continua__data_final__gte=data,
            inclusao_alimentacao_continua__dias_semana__contains=[data.weekday()],
            inclusao_alimentacao_continua__status=PedidoAPartirDaEscolaWorkflow.CODAE_AUTORIZADO
        )
        |
        Q(
            grupo_inclusao_normal__escola=escola_periodo_escolar.escola,
            grupo_inclusao_normal__inclusoes_normais__data=data,
            grupo_inclusao_normal__status=PedidoAPartirDaEscolaWorkflow.CODAE_AUTORIZADO
        ),
        periodo_escolar=escola_periodo_escolar.periodo_escolar,
        tipos_alimentacao__tipos_alimentacao__nome__iexact='merenda seca'
    ).aggregate(total_merendas_secas=Sum('numero_alunos'))['total_merendas_secas']
    return total_merendas_secas if total_merendas_secas is not None else 0


def total_kits_lanche_por_escola_e_data(escola, data):
    total_kits = SolicitacaoKitLancheAvulsa.objects.filter(
        escola=escola,
        solicitacao_kit_lanche__data=data,
        status=PedidoAPartirDaEscolaWorkflow.CODAE_AUTORIZADO
    ).annotate(total_kits=F('quantidade_alunos') * Count('solicitacao_kit_lanche__kits')
    ).aggregate(Sum('total_kits'))['total_kits__sum']
    return total_kits if total_kits is not None else 0
