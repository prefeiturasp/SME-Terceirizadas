import calendar
import datetime

from django.db.models import Q

from sme_terceirizadas.dados_comuns.utils import get_ultimo_dia_mes

from ..cardapio.models import VinculoTipoAlimentacaoComPeriodoEscolarETipoUnidadeEscolar
from ..dieta_especial.models import (
    ClassificacaoDieta,
    LogQuantidadeDietasAutorizadasCEI,
)
from ..escola.models import (
    DiaCalendario,
    FaixaEtaria,
    LogAlunosMatriculadosFaixaEtariaDia,
)
from ..inclusao_alimentacao.models import (
    GrupoInclusaoAlimentacaoNormal,
    InclusaoAlimentacaoNormal,
)
from ..paineis_consolidados.models import SolicitacoesEscola
from .models import CategoriaMedicao, PermissaoLancamentoEspecial, ValorMedicao


def get_nome_campo(campo):
    campos = {
        "Número de Alunos": "numero_de_alunos",
        "Matriculados": "matriculados",
        "Frequência": "frequencia",
        "Solicitado": "solicitado",
        "Desjejum": "desjejum",
        "Lanche": "lanche",
        "Lanche 4h": "lanche_4h",
        "Refeição": "refeicao",
        "Repetição de Refeição": "repeticao_refeicao",
        "Sobremesa": "sobremesa",
        "Repetição de Sobremesa": "repeticao_sobremesa",
        "2º Lanche 4h": "2_lanche_4h",
        "2º Lanche 5h": "2_lanche_5h",
        "Lanche Extra": "lanche_extra",
        "2ª Refeição 1ª oferta": "2_refeicao_1_oferta",
        "Repetição 2ª Refeição": "repeticao_2_refeicao",
        "2ª Sobremesa 1ª oferta": "2_sobremesa_1_oferta",
        "Repetição 2ª Sobremesa": "repeticao_2_sobremesa",
    }
    return campos.get(campo, campo)


def get_lista_dias_letivos(solicitacao, escola):
    dias_letivos = DiaCalendario.objects.filter(
        data__month=int(solicitacao.mes),
        data__year=int(solicitacao.ano),
        escola=escola,
        dia_letivo=True,
    )
    dias_letivos = list(set(dias_letivos.values_list("data__day", flat=True)))
    return [
        str(dia) if not len(str(dia)) == 1 else ("0" + str(dia)) for dia in dias_letivos
    ]


def erros_unicos(lista_erros):
    return list(map(dict, set(tuple(sorted(erro.items())) for erro in lista_erros)))


def buscar_valores_lancamento_alimentacoes(
    linhas_da_tabela,
    solicitacao,
    periodo_escolar,
    dias_letivos,
    categoria_medicao,
    lista_erros,
):
    periodo_com_erro = False
    for nome_campo in linhas_da_tabela:
        valores_da_medicao = (
            ValorMedicao.objects.filter(
                medicao__solicitacao_medicao_inicial=solicitacao,
                nome_campo=nome_campo,
                medicao__periodo_escolar=periodo_escolar,
                dia__in=dias_letivos,
                categoria_medicao=categoria_medicao,
            )
            .exclude(valor=None)
            .values_list("dia", flat=True)
        )
        valores_da_medicao = list(set(valores_da_medicao))
        if len(valores_da_medicao) != len(dias_letivos):
            diferenca = list(set(dias_letivos) - set(valores_da_medicao))
            for dia_sem_preenchimento in diferenca:
                valor_observacao = ValorMedicao.objects.filter(
                    medicao__solicitacao_medicao_inicial=solicitacao,
                    nome_campo="observacao",
                    medicao__periodo_escolar=periodo_escolar,
                    dia=dia_sem_preenchimento,
                    categoria_medicao=categoria_medicao,
                ).exclude(valor=None)
                if not valor_observacao:
                    periodo_com_erro = True
    if periodo_com_erro:
        lista_erros.append(
            {
                "periodo_escolar": periodo_escolar.nome,
                "erro": "Restam dias a serem lançados nas alimentações.",
            }
        )
    return lista_erros


def validate_lancamento_alimentacoes_medicao(solicitacao, lista_erros):
    escola = solicitacao.escola
    tipo_unidade = escola.tipo_unidade
    categoria_medicao = CategoriaMedicao.objects.get(nome="ALIMENTAÇÃO")
    dias_letivos = get_lista_dias_letivos(solicitacao, escola)
    for periodo_escolar in escola.periodos_escolares(solicitacao.ano):
        permissoes_especiais = PermissaoLancamentoEspecial.objects.filter(
            Q(
                data_inicial__month__lte=int(solicitacao.mes),
                data_inicial__year=int(solicitacao.ano),
                data_final=None,
            )
            | Q(
                data_inicial__month__lte=int(solicitacao.mes),
                data_inicial__year=int(solicitacao.ano),
                data_final__month=int(solicitacao.mes),
                data_final__year=int(solicitacao.ano),
            ),
            escola=escola,
            periodo_escolar=periodo_escolar,
        )
        alimentacoes_permitidas = list(
            set(
                [
                    nome
                    for nome, ativo in permissoes_especiais.values_list(
                        "alimentacoes_lancamento_especial__nome",
                        "alimentacoes_lancamento_especial__ativo",
                    )
                    if ativo
                ]
            )
        )
        vinculo = (
            VinculoTipoAlimentacaoComPeriodoEscolarETipoUnidadeEscolar.objects.get(
                tipo_unidade_escolar=tipo_unidade, periodo_escolar=periodo_escolar
            )
        )
        alimentacoes_vinculadas = vinculo.tipos_alimentacao.exclude(
            nome="Lanche Emergencial"
        )
        alimentacoes_vinculadas = list(
            set(alimentacoes_vinculadas.values_list("nome", flat=True))
        )
        alimentacoes = alimentacoes_vinculadas + alimentacoes_permitidas
        linhas_da_tabela = ["matriculados", "frequencia"]
        for alimentacao in alimentacoes:
            nome_formatado = get_nome_campo(alimentacao)
            linhas_da_tabela.append(nome_formatado)
            if nome_formatado == "refeicao":
                linhas_da_tabela.append("repeticao_refeicao")
            if nome_formatado == "sobremesa":
                linhas_da_tabela.append("repeticao_sobremesa")

        lista_erros = buscar_valores_lancamento_alimentacoes(
            linhas_da_tabela,
            solicitacao,
            periodo_escolar,
            dias_letivos,
            categoria_medicao,
            lista_erros,
        )
    return erros_unicos(lista_erros)


def lista_erros_com_periodo(lista_erros, medicao, tipo_erro):
    return next(
        (
            erro
            for erro in lista_erros
            if (
                erro["periodo_escolar"] == medicao.periodo_escolar.nome
                if medicao.periodo_escolar
                else medicao.grupo.nome
            )
            and tipo_erro in erro["erro"]
        ),
        None,
    )


def validate_lancamento_alimentacoes_medicao_cei_faixas_etarias(
    faixas_etarias,
    lista_erros,
    medicao,
    logs_,
    ano,
    mes,
    dia,
    categoria,
    periodo_com_erro,
    valores_medicao_,
):
    DATA_INDEX = 0
    PERIODO_ESCOLAR_ID_INDEX = 1
    FAIXA_ETARIA_ID_INDEX = 2
    QUANTIDADE_INDEX = 3

    NOME_CAMPO_INDEX = 0
    CATEGORIA_MEDICAO_ID_INDEX = 1
    DIA_ID = 3

    for faixa_etaria in faixas_etarias:
        if lista_erros_com_periodo(lista_erros, medicao, "alimentações"):
            continue
        log = next(
            (
                log_
                for log_ in logs_
                if (
                    log_[DATA_INDEX] == datetime.date(int(ano), int(mes), int(dia))
                    and log_[PERIODO_ESCOLAR_ID_INDEX] == medicao.periodo_escolar.id
                    and log_[FAIXA_ETARIA_ID_INDEX] == faixa_etaria.id
                )
            ),
            None,
        )
        quantidade = log[QUANTIDADE_INDEX] if log else 0
        if quantidade == 0:
            continue
        valor_medicao = next(
            (
                valor_medicao_
                for valor_medicao_ in valores_medicao_
                if (
                    valor_medicao_[NOME_CAMPO_INDEX] == "frequencia"
                    and valor_medicao_[CATEGORIA_MEDICAO_ID_INDEX] == categoria.id
                    and valor_medicao_[FAIXA_ETARIA_ID_INDEX] == faixa_etaria.id
                    and valor_medicao_[DIA_ID] == f"{dia:02d}"
                )
            ),
            None,
        )
        if not valor_medicao:
            periodo_com_erro = True
    return periodo_com_erro


def build_nomes_campos_dietas_emef(escola, categoria, medicao):
    tipos_alimentacao = list(
        VinculoTipoAlimentacaoComPeriodoEscolarETipoUnidadeEscolar.objects.filter(
            tipo_unidade_escolar=escola.tipo_unidade,
            periodo_escolar__in=escola.periodos_escolares(
                medicao.solicitacao_medicao_inicial.ano
            ),
        )
        .values_list("tipos_alimentacao__nome", flat=True)
        .distinct()
    )

    nomes_campos = ["frequencia"]
    if "Lanche" in tipos_alimentacao:
        nomes_campos.append("lanche")
    if "Lanche 4h" in tipos_alimentacao:
        nomes_campos.append("lanche_4h")
    if "Refeição" in tipos_alimentacao and "ENTERAL" in categoria.nome:
        nomes_campos.append("refeicao")
    return nomes_campos


def build_nomes_campos_inclusoes_dietas_emef(escola, categoria, inclusoes, medicao):
    tipos_alimentacao = list(
        VinculoTipoAlimentacaoComPeriodoEscolarETipoUnidadeEscolar.objects.filter(
            tipo_unidade_escolar=escola.tipo_unidade,
            periodo_escolar__in=escola.periodos_escolares(
                medicao.solicitacao_medicao_inicial.ano
            ),
        )
        .values_list("tipos_alimentacao__nome", flat=True)
        .distinct()
    )

    nomes_campos = ["frequencia"]
    if (
        "Lanche" in tipos_alimentacao
        and inclusoes.filter(
            quantidades_por_periodo__periodo_escolar=medicao.periodo_escolar,
            quantidades_por_periodo__tipos_alimentacao__nome="Lanche",
        ).exists()
    ):
        nomes_campos.append("lanche")
    if (
        "Lanche 4h" in tipos_alimentacao
        and inclusoes.filter(
            quantidades_por_periodo__periodo_escolar=medicao.periodo_escolar,
            quantidades_por_periodo__tipos_alimentacao__nome="Lanche 4h",
        ).exists()
    ):
        nomes_campos.append("lanche_4h")
    if (
        "Refeição" in tipos_alimentacao
        and "ENTERAL" in categoria.nome
        and inclusoes.filter(
            quantidades_por_periodo__periodo_escolar=medicao.periodo_escolar,
            quantidades_por_periodo__tipos_alimentacao__nome="Refeição",
        ).exists()
    ):
        nomes_campos.append("refeicao")
    return nomes_campos


def get_nomes_campos_emef_dietas(inclusoes, escola, categoria, medicao):
    if inclusoes:
        return build_nomes_campos_inclusoes_dietas_emef(
            escola, categoria, inclusoes, medicao
        )
    else:
        return build_nomes_campos_dietas_emef(escola, categoria, medicao)


def validate_lancamento_alimentacoes_medicao_emef_dietas(
    lista_erros,
    medicao,
    logs_,
    ano,
    mes,
    dia,
    categoria,
    classificacoes,
    periodo_com_erro,
    valores_medicao_,
    escola,
    inclusoes=None,
):
    DATA_INDEX = 0
    PERIODO_ESCOLAR_ID_INDEX = 1
    QUANTIDADE_INDEX = 2
    CLASSIFICACAO_ID_INDEX = 3

    NOME_CAMPO_INDEX = 0
    CATEGORIA_MEDICAO_ID_INDEX = 1
    DIA_ID = 2

    nomes_campos = get_nomes_campos_emef_dietas(inclusoes, escola, categoria, medicao)
    for nome_campo in nomes_campos:
        if lista_erros_com_periodo(lista_erros, medicao, "dietas"):
            continue
        quantidade = 0
        for classificacao in classificacoes:
            log = next(
                (
                    log_
                    for log_ in logs_
                    if (
                        log_[DATA_INDEX] == datetime.date(int(ano), int(mes), int(dia))
                        and (
                            log_[PERIODO_ESCOLAR_ID_INDEX] == medicao.periodo_escolar.id
                            if medicao.periodo_escolar
                            else None
                        )
                        and log_[CLASSIFICACAO_ID_INDEX] == classificacao.id
                    )
                ),
                None,
            )
            quantidade += log[QUANTIDADE_INDEX] if log else 0
        if quantidade == 0:
            continue
        valor_medicao = next(
            (
                valor_medicao_
                for valor_medicao_ in valores_medicao_
                if (
                    valor_medicao_[NOME_CAMPO_INDEX] == nome_campo
                    and valor_medicao_[CATEGORIA_MEDICAO_ID_INDEX] == categoria.id
                    and valor_medicao_[DIA_ID] == f"{dia:02d}"
                )
            ),
            None,
        )
        if not valor_medicao:
            periodo_com_erro = True
    return periodo_com_erro


def validate_lancamento_alimentacoes_medicao_cei_dietas_faixas_etarias(
    faixas_etarias,
    lista_erros,
    medicao,
    logs_,
    ano,
    mes,
    dia,
    categoria,
    classificacoes,
    periodo_com_erro,
    valores_medicao_,
):
    DATA_INDEX = 0
    PERIODO_ESCOLAR_ID_INDEX = 1
    FAIXA_ETARIA_ID_INDEX = 2
    QUANTIDADE_INDEX = 3
    CLASSIFICACAO_ID_INDEX = 4

    NOME_CAMPO_INDEX = 0
    CATEGORIA_MEDICAO_ID_INDEX = 1
    DIA_ID = 3

    for faixa_etaria in faixas_etarias:
        if lista_erros_com_periodo(lista_erros, medicao, "dietas"):
            continue
        quantidade = 0
        for classificacao in classificacoes:
            log = next(
                (
                    log_
                    for log_ in logs_
                    if (
                        log_[DATA_INDEX] == datetime.date(int(ano), int(mes), int(dia))
                        and log_[PERIODO_ESCOLAR_ID_INDEX] == medicao.periodo_escolar.id
                        and log_[FAIXA_ETARIA_ID_INDEX] == faixa_etaria.id
                        and log_[CLASSIFICACAO_ID_INDEX] == classificacao.id
                    )
                ),
                None,
            )
            quantidade += log[QUANTIDADE_INDEX] if log else 0
        if quantidade == 0:
            continue
        valor_medicao = next(
            (
                valor_medicao_
                for valor_medicao_ in valores_medicao_
                if (
                    valor_medicao_[NOME_CAMPO_INDEX] == "frequencia"
                    and valor_medicao_[CATEGORIA_MEDICAO_ID_INDEX] == categoria.id
                    and valor_medicao_[FAIXA_ETARIA_ID_INDEX] == faixa_etaria.id
                    and valor_medicao_[DIA_ID] == f"{dia:02d}"
                )
            ),
            None,
        )
        if not valor_medicao:
            periodo_com_erro = True
    return periodo_com_erro


def valida_medicoes_inexistentes_cei(solicitacao, lista_erros):
    for periodo_escolar_nome in solicitacao.escola.periodos_escolares_com_alunos:
        if not solicitacao.medicoes.filter(
            periodo_escolar__nome=periodo_escolar_nome
        ).exists():
            lista_erros.append(
                {
                    "periodo_escolar": periodo_escolar_nome,
                    "erro": "Restam dias a serem lançados nas alimentações.",
                }
            )
    if (
        solicitacao.ue_possui_alunos_periodo_parcial
        and not solicitacao.medicoes.filter(periodo_escolar__nome="PARCIAL").exists()
    ):
        lista_erros.append(
            {
                "periodo_escolar": "PARCIAL",
                "erro": "Restam dias a serem lançados nas alimentações.",
            }
        )
    return lista_erros


def validate_lancamento_alimentacoes_medicao_cei(solicitacao, lista_erros):
    ano = solicitacao.ano
    mes = solicitacao.mes
    escola = solicitacao.escola
    categoria = CategoriaMedicao.objects.get(nome="ALIMENTAÇÃO")
    faixas_etarias = FaixaEtaria.objects.filter(ativo=True)
    logs = LogAlunosMatriculadosFaixaEtariaDia.objects.filter(
        escola=escola, data__month=mes, data__year=ano
    )
    dias_letivos = list(
        DiaCalendario.objects.filter(
            escola=escola, data__month=mes, data__year=ano, dia_letivo=True
        ).values_list("data__day", flat=True)
    )

    logs_ = list(
        set(
            logs.values_list(
                "data", "periodo_escolar_id", "faixa_etaria_id", "quantidade"
            ).distinct()
        )
    )

    for dia in dias_letivos:
        for medicao in solicitacao.medicoes.all():
            valores_medicao_ = list(
                set(
                    medicao.valores_medicao.values_list(
                        "nome_campo",
                        "categoria_medicao_id",
                        "faixa_etaria_id",
                        "dia",
                    )
                )
            )
            periodo_com_erro = False
            if lista_erros_com_periodo(lista_erros, medicao, "alimentações"):
                continue
            periodo_com_erro = (
                validate_lancamento_alimentacoes_medicao_cei_faixas_etarias(
                    faixas_etarias,
                    lista_erros,
                    medicao,
                    logs_,
                    ano,
                    mes,
                    dia,
                    categoria,
                    periodo_com_erro,
                    valores_medicao_,
                )
            )
            if periodo_com_erro:
                lista_erros.append(
                    {
                        "periodo_escolar": medicao.periodo_escolar.nome,
                        "erro": "Restam dias a serem lançados nas alimentações.",
                    }
                )
    return lista_erros


def buscar_valores_lancamento_inclusoes(
    inclusao, solicitacao, categoria_medicao, lista_erros
):
    periodo_com_erro = False
    for nome_campo in inclusao["linhas_da_tabela"]:
        valores_da_medicao = ValorMedicao.objects.filter(
            medicao__solicitacao_medicao_inicial=solicitacao,
            nome_campo=nome_campo,
            medicao__periodo_escolar__nome=inclusao["periodo_escolar"],
            dia=inclusao["dia"],
            categoria_medicao=categoria_medicao,
        ).exclude(valor=None)
        if not valores_da_medicao:
            valor_observacao = ValorMedicao.objects.filter(
                medicao__solicitacao_medicao_inicial=solicitacao,
                nome_campo="observacao",
                medicao__periodo_escolar__nome=inclusao["periodo_escolar"],
                dia=inclusao["dia"],
                categoria_medicao=categoria_medicao,
            ).exclude(valor=None)
            if not valor_observacao:
                periodo_com_erro = True
    if periodo_com_erro:
        lista_erros.append(
            {
                "periodo_escolar": inclusao["periodo_escolar"],
                "erro": "Restam dias a serem lançados nas alimentações.",
            }
        )
    return lista_erros


def validate_lancamento_inclusoes(solicitacao, lista_erros):
    escola = solicitacao.escola
    categoria_medicao = CategoriaMedicao.objects.get(nome="ALIMENTAÇÃO")
    list_inclusoes = []

    inclusoes_uuids = list(
        set(
            GrupoInclusaoAlimentacaoNormal.objects.filter(
                escola=escola,
                status=GrupoInclusaoAlimentacaoNormal.workflow_class.CODAE_AUTORIZADO,
            ).values_list("inclusoes_normais__uuid", flat=True)
        )
    )
    inclusoes = InclusaoAlimentacaoNormal.objects.filter(
        uuid__in=inclusoes_uuids,
        data__month=int(solicitacao.mes),
        data__year=int(solicitacao.ano),
        cancelado=False,
    ).order_by("data")

    for inclusao in inclusoes:
        grupo = inclusao.grupo_inclusao
        for periodo in grupo.quantidades_periodo.all():
            tipos_alimentacao = periodo.tipos_alimentacao.exclude(
                nome="Lanche Emergencial"
            )
            tipos_alimentacao = list(
                set(tipos_alimentacao.values_list("nome", flat=True))
            )
            tipos_alimentacao = [
                get_nome_campo(alimentacao) for alimentacao in tipos_alimentacao
            ]

            dia_da_inclusao = str(inclusao.data.day)
            if len(dia_da_inclusao) == 1:
                dia_da_inclusao = "0" + str(inclusao.data.day)
            list_inclusoes.append(
                {
                    "periodo_escolar": periodo.periodo_escolar.nome,
                    "dia": dia_da_inclusao,
                    "linhas_da_tabela": tipos_alimentacao,
                }
            )
    for inclusao in list_inclusoes:
        lista_erros = buscar_valores_lancamento_inclusoes(
            inclusao, solicitacao, categoria_medicao, lista_erros
        )
    return erros_unicos(lista_erros)


def get_inclusoes_filtradas_cei(inclusoes, dia, mes, ano, medicao):
    inclusoes_ = inclusoes.filter(
        dias_motivos_da_inclusao_cei__data=datetime.date(int(ano), int(mes), int(dia)),
        dias_motivos_da_inclusao_cei__cancelado=False,
    )
    if medicao.periodo_escolar.nome == "PARCIAL":
        inclusoes_ = inclusoes_.filter(
            quantidade_alunos_da_inclusao__periodo_externo__nome="INTEGRAL"
        ).exclude(quantidade_alunos_da_inclusao__periodo__nome="INTEGRAL")
    else:
        inclusoes_ = inclusoes_.filter(
            quantidade_alunos_da_inclusao__periodo=medicao.periodo_escolar,
            quantidade_alunos_da_inclusao__periodo_externo=medicao.periodo_escolar,
        )
    return inclusoes_


def get_inclusoes_filtradas_emef(inclusoes, dia, mes, ano, medicao):
    inclusoes_ = inclusoes.filter(
        inclusoes_normais__data=datetime.date(int(ano), int(mes), int(dia)),
        inclusoes_normais__cancelado=False,
        quantidades_por_periodo__periodo_escolar=medicao.periodo_escolar,
    )
    return inclusoes_


def get_lista_erros_inclusoes_cei(
    dias_nao_letivos,
    solicitacao,
    lista_erros,
    inclusoes,
    mes,
    ano,
    faixas_etarias,
    categoria,
    logs,
):
    logs_ = list(
        set(
            logs.values_list(
                "data", "periodo_escolar_id", "faixa_etaria_id", "quantidade"
            ).distinct()
        )
    )
    for dia in dias_nao_letivos:
        for medicao in solicitacao.medicoes.all():
            valores_medicao_ = list(
                set(
                    medicao.valores_medicao.values_list(
                        "nome_campo",
                        "categoria_medicao_id",
                        "faixa_etaria_id",
                        "dia",
                    )
                )
            )
            periodo_com_erro = False
            if lista_erros_com_periodo(lista_erros, medicao, "alimentações"):
                continue
            inclusoes_ = get_inclusoes_filtradas_cei(inclusoes, dia, mes, ano, medicao)
            if not inclusoes_.exists():
                continue
            periodo_com_erro = (
                validate_lancamento_alimentacoes_medicao_cei_faixas_etarias(
                    faixas_etarias,
                    lista_erros,
                    medicao,
                    logs_,
                    ano,
                    mes,
                    dia,
                    categoria,
                    periodo_com_erro,
                    valores_medicao_,
                )
            )
            if periodo_com_erro:
                lista_erros.append(
                    {
                        "periodo_escolar": medicao.periodo_escolar.nome,
                        "erro": "Restam dias a serem lançados nas alimentações.",
                    }
                )
    return lista_erros


def get_lista_erros_inclusoes_dietas_emef(
    dias_nao_letivos,
    solicitacao,
    lista_erros,
    inclusoes,
    mes,
    ano,
    categoria,
    logs,
):
    logs_ = list(
        set(
            logs.values_list(
                "data",
                "periodo_escolar_id",
                "quantidade",
                "classificacao_id",
            ).distinct()
        )
    )
    classificacoes = get_classificacoes_dietas(categoria)
    for dia in dias_nao_letivos:
        for medicao in solicitacao.medicoes.filter(periodo_escolar__isnull=False):
            valores_medicao_ = list(
                set(
                    medicao.valores_medicao.values_list(
                        "nome_campo",
                        "categoria_medicao_id",
                        "dia",
                    )
                )
            )
            periodo_com_erro = False
            if lista_erros_com_periodo(lista_erros, medicao, "dietas"):
                continue
            inclusoes_ = get_inclusoes_filtradas_emef(inclusoes, dia, mes, ano, medicao)
            if not inclusoes_.exists():
                continue
            periodo_com_erro = validate_lancamento_alimentacoes_medicao_emef_dietas(
                lista_erros,
                medicao,
                logs_,
                ano,
                mes,
                dia,
                categoria,
                classificacoes,
                periodo_com_erro,
                valores_medicao_,
                solicitacao.escola,
                inclusoes_,
            )
            if periodo_com_erro:
                lista_erros.append(
                    {
                        "periodo_escolar": medicao.periodo_escolar.nome,
                        "erro": "Restam dias a serem lançados nas dietas.",
                    }
                )
    return lista_erros


def get_lista_erros_inclusoes_dietas_cei(
    dias_nao_letivos,
    solicitacao,
    lista_erros,
    inclusoes,
    mes,
    ano,
    faixas_etarias,
    categoria,
    classificacao,
    logs,
):
    logs_ = list(
        set(
            logs.values_list(
                "data",
                "periodo_escolar_id",
                "faixa_etaria_id",
                "quantidade",
                "classificacao_id",
            ).distinct()
        )
    )
    for dia in dias_nao_letivos:
        for medicao in solicitacao.medicoes.all():
            valores_medicao_ = list(
                set(
                    medicao.valores_medicao.values_list(
                        "nome_campo",
                        "categoria_medicao_id",
                        "faixa_etaria_id",
                        "dia",
                    )
                )
            )
            periodo_com_erro = False
            if lista_erros_com_periodo(lista_erros, medicao, "dietas"):
                continue
            inclusoes_ = get_inclusoes_filtradas_cei(inclusoes, dia, mes, ano, medicao)
            if not inclusoes_.exists():
                continue
            periodo_com_erro = (
                validate_lancamento_alimentacoes_medicao_cei_dietas_faixas_etarias(
                    faixas_etarias,
                    lista_erros,
                    medicao,
                    logs_,
                    ano,
                    mes,
                    dia,
                    categoria,
                    classificacao,
                    periodo_com_erro,
                    valores_medicao_,
                )
            )
            if periodo_com_erro:
                lista_erros.append(
                    {
                        "periodo_escolar": medicao.periodo_escolar.nome,
                        "erro": "Restam dias a serem lançados nas dietas.",
                    }
                )
    return lista_erros


def validate_lancamento_inclusoes_cei(solicitacao, lista_erros):
    escola = solicitacao.escola
    mes = solicitacao.mes
    ano = solicitacao.ano

    inclusoes = (
        escola.inclusao_alimentacao_inclusaoalimentacaodacei_rastro_escola.filter(
            dias_motivos_da_inclusao_cei__data__month=mes,
            dias_motivos_da_inclusao_cei__data__year=ano,
            dias_motivos_da_inclusao_cei__cancelado=False,
            status="CODAE_AUTORIZADO",
        )
    )
    if not inclusoes.exists():
        return lista_erros

    categoria = CategoriaMedicao.objects.get(nome="ALIMENTAÇÃO")
    faixas_etarias = FaixaEtaria.objects.filter(ativo=True)
    logs = LogAlunosMatriculadosFaixaEtariaDia.objects.filter(
        escola=escola, data__month=mes, data__year=ano
    )
    dias_nao_letivos = list(
        DiaCalendario.objects.filter(
            escola=escola, data__month=mes, data__year=ano, dia_letivo=False
        ).values_list("data__day", flat=True)
    )

    lista_erros = get_lista_erros_inclusoes_cei(
        dias_nao_letivos,
        solicitacao,
        lista_erros,
        inclusoes,
        mes,
        ano,
        faixas_etarias,
        categoria,
        logs,
    )

    return lista_erros


def validate_lancamento_inclusoes_dietas_emef(solicitacao, lista_erros):
    escola = solicitacao.escola
    mes = solicitacao.mes
    ano = solicitacao.ano

    inclusoes = escola.grupos_inclusoes_normais.filter(
        inclusoes_normais__data__month=mes,
        inclusoes_normais__data__year=ano,
        inclusoes_normais__cancelado=False,
        status="CODAE_AUTORIZADO",
    )
    if not inclusoes.exists():
        return lista_erros

    logs = escola.logs_dietas_autorizadas.filter(data__month=mes, data__year=ano)
    dias_nao_letivos = list(
        DiaCalendario.objects.filter(
            escola=escola, data__month=mes, data__year=ano, dia_letivo=False
        ).values_list("data__day", flat=True)
    )
    categorias = CategoriaMedicao.objects.exclude(nome__icontains="ALIMENTAÇÃO")
    for categoria in categorias:
        lista_erros = get_lista_erros_inclusoes_dietas_emef(
            dias_nao_letivos,
            solicitacao,
            lista_erros,
            inclusoes,
            mes,
            ano,
            categoria,
            logs,
        )
    return lista_erros


def validate_lancamento_inclusoes_dietas_cei(solicitacao, lista_erros):
    escola = solicitacao.escola
    mes = solicitacao.mes
    ano = solicitacao.ano

    inclusoes = (
        escola.inclusao_alimentacao_inclusaoalimentacaodacei_rastro_escola.filter(
            dias_motivos_da_inclusao_cei__data__month=mes,
            dias_motivos_da_inclusao_cei__data__year=ano,
            dias_motivos_da_inclusao_cei__cancelado=False,
            status="CODAE_AUTORIZADO",
        )
    )
    if not inclusoes.exists():
        return lista_erros

    faixas_etarias = FaixaEtaria.objects.filter(ativo=True)
    logs = LogQuantidadeDietasAutorizadasCEI.objects.filter(
        escola=escola, data__month=mes, data__year=ano
    )
    dias_nao_letivos = list(
        DiaCalendario.objects.filter(
            escola=escola, data__month=mes, data__year=ano, dia_letivo=False
        ).values_list("data__day", flat=True)
    )
    categorias = CategoriaMedicao.objects.exclude(
        nome__icontains="ALIMENTAÇÃO"
    ).exclude(nome__icontains="ENTERAL")
    for categoria in categorias:
        classificacao = get_classificacoes_dietas_cei(categoria)
        lista_erros = get_lista_erros_inclusoes_dietas_cei(
            dias_nao_letivos,
            solicitacao,
            lista_erros,
            inclusoes,
            mes,
            ano,
            faixas_etarias,
            categoria,
            classificacao,
            logs,
        )
    return lista_erros


def get_classificacoes_dietas_cei(categoria):
    classificacoes = ClassificacaoDieta.objects.filter(
        nome__icontains=categoria.nome.split(" - ")[1]
    )
    return classificacoes


def get_classificacoes_dietas(categoria):
    if "AMINOÁCIDOS" in categoria.nome:
        classificacoes = ClassificacaoDieta.objects.filter(
            nome__icontains="Tipo A"
        ).exclude(nome="Tipo A")
    else:
        classificacoes = (
            ClassificacaoDieta.objects.filter(
                nome__icontains=categoria.nome.split(" - ")[1]
            )
            .exclude(nome__icontains="amino")
            .exclude(nome__icontains="enteral")
        )
    return classificacoes


def validate_lancamento_dietas_emef(solicitacao, lista_erros):
    ano = solicitacao.ano
    mes = solicitacao.mes
    escola = solicitacao.escola
    categorias = CategoriaMedicao.objects.exclude(nome__icontains="ALIMENTAÇÃO")
    logs = escola.logs_dietas_autorizadas.filter(data__month=mes, data__year=ano)
    logs_ = list(
        set(
            logs.values_list(
                "data",
                "periodo_escolar_id",
                "quantidade",
                "classificacao_id",
            ).distinct()
        )
    )
    dias_letivos = list(
        DiaCalendario.objects.filter(
            escola=escola, data__month=mes, data__year=ano, dia_letivo=True
        ).values_list("data__day", flat=True)
    )
    for categoria in categorias:
        classificacoes = get_classificacoes_dietas(categoria)
        for dia in dias_letivos:
            for medicao in solicitacao.medicoes.all():
                valores_medicao_ = list(
                    set(
                        medicao.valores_medicao.values_list(
                            "nome_campo",
                            "categoria_medicao_id",
                            "dia",
                        )
                    )
                )
                periodo_com_erro = False
                if lista_erros_com_periodo(lista_erros, medicao, "dietas"):
                    continue
                periodo_com_erro = validate_lancamento_alimentacoes_medicao_emef_dietas(
                    lista_erros,
                    medicao,
                    logs_,
                    ano,
                    mes,
                    dia,
                    categoria,
                    classificacoes,
                    periodo_com_erro,
                    valores_medicao_,
                    escola,
                )
                if periodo_com_erro:
                    lista_erros.append(
                        {
                            "periodo_escolar": medicao.periodo_escolar.nome,
                            "erro": "Restam dias a serem lançados nas dietas.",
                        }
                    )
    return lista_erros


def validate_lancamento_dietas_cei(solicitacao, lista_erros):
    ano = solicitacao.ano
    mes = solicitacao.mes
    escola = solicitacao.escola
    categorias = CategoriaMedicao.objects.exclude(
        nome__icontains="ALIMENTAÇÃO"
    ).exclude(nome__icontains="ENTERAL")
    faixas_etarias = FaixaEtaria.objects.filter(ativo=True)
    logs = LogQuantidadeDietasAutorizadasCEI.objects.filter(
        escola=escola, data__month=mes, data__year=ano
    )
    logs_ = list(
        set(
            logs.values_list(
                "data",
                "periodo_escolar_id",
                "faixa_etaria_id",
                "quantidade",
                "classificacao_id",
            ).distinct()
        )
    )
    dias_letivos = list(
        DiaCalendario.objects.filter(
            escola=escola, data__month=mes, data__year=ano, dia_letivo=True
        ).values_list("data__day", flat=True)
    )
    for categoria in categorias:
        classificacoes = get_classificacoes_dietas_cei(categoria)
        for dia in dias_letivos:
            for medicao in solicitacao.medicoes.all():
                valores_medicao_ = list(
                    set(
                        medicao.valores_medicao.values_list(
                            "nome_campo",
                            "categoria_medicao_id",
                            "faixa_etaria_id",
                            "dia",
                        )
                    )
                )
                periodo_com_erro = False
                if lista_erros_com_periodo(lista_erros, medicao, "dietas"):
                    continue
                periodo_com_erro = (
                    validate_lancamento_alimentacoes_medicao_cei_dietas_faixas_etarias(
                        faixas_etarias,
                        lista_erros,
                        medicao,
                        logs_,
                        ano,
                        mes,
                        dia,
                        categoria,
                        classificacoes,
                        periodo_com_erro,
                        valores_medicao_,
                    )
                )
                if periodo_com_erro:
                    lista_erros.append(
                        {
                            "periodo_escolar": medicao.periodo_escolar.nome,
                            "erro": "Restam dias a serem lançados nas dietas.",
                        }
                    )
    return lista_erros


def remover_duplicados(query_set):
    aux = []
    sem_uuid_repetido = []
    for resultado in query_set:
        if resultado.uuid not in aux:
            aux.append(resultado.uuid)
            sem_uuid_repetido.append(resultado)
    return sem_uuid_repetido


def formatar_query_set_alteracao(query_set, mes, ano):
    datas = []
    for alteracao_alimentacao in query_set:
        alteracao = alteracao_alimentacao.get_raw_model.objects.get(
            uuid=alteracao_alimentacao.uuid
        )
        datas_intervalos = alteracao.datas_intervalo.filter(
            data__month=mes, data__year=ano, cancelado=False
        )
        for obj in datas_intervalos:
            if not len(str(obj.data.day)) == 1:
                datas.append(str(obj.data.day))
            else:
                datas.append(("0" + str(obj.data.day)))
    return list(set(datas))


def get_lista_dias_solicitacoes(params, escola):
    query_set = SolicitacoesEscola.get_autorizados(escola_uuid=escola.uuid)
    query_set = SolicitacoesEscola.busca_filtro(query_set, params)
    query_set = query_set.filter(
        data_evento__month=params["mes"], data_evento__year=params["ano"]
    )
    query_set = query_set.filter(data_evento__lt=datetime.date.today())
    if params.get("eh_lanche_emergencial", False):
        query_set = query_set.filter(motivo__icontains="Emergencial")
        query_set = remover_duplicados(query_set)
        return formatar_query_set_alteracao(query_set, params["mes"], params["ano"])
    else:
        query_set = remover_duplicados(query_set)
        datas_kits = []
        for obj in query_set:
            if not len(str(obj.data_evento.day)) == 1:
                datas_kits.append(str(obj.data_evento.day))
            else:
                datas_kits.append(("0" + str(obj.data_evento.day)))
        return datas_kits


def validate_lancamento_kit_lanche(solicitacao, lista_erros):
    escola = solicitacao.escola
    mes = solicitacao.mes
    ano = solicitacao.ano
    tipo_solicitacao = "Kit Lanche"
    params = {
        "mes": mes,
        "ano": ano,
        "escola_uuid": escola.uuid,
        "tipo_solicitacao": tipo_solicitacao,
    }
    dias_kit_lanche = get_lista_dias_solicitacoes(params, escola)
    dias_kit_lanche = list(set(dias_kit_lanche))

    valores_da_medicao = (
        ValorMedicao.objects.filter(
            medicao__solicitacao_medicao_inicial=solicitacao,
            nome_campo="kit_lanche",
            medicao__grupo__nome="Solicitações de Alimentação",
            dia__in=dias_kit_lanche,
        )
        .order_by("dia")
        .exclude(valor=None)
        .values_list("dia", flat=True)
    )
    valores_da_medicao = list(set(valores_da_medicao))
    if len(valores_da_medicao) != len(dias_kit_lanche):
        lista_erros.append(
            {
                "periodo_escolar": "Solicitações de Alimentação",
                "erro": "Restam dias a serem lançados nos Kit Lanches.",
            }
        )
    return erros_unicos(lista_erros)


def validate_lanche_emergencial(solicitacao, lista_erros):
    escola = solicitacao.escola
    mes = solicitacao.mes
    ano = solicitacao.ano
    tipo_solicitacao = "Alteração"
    eh_lanche_emergencial = True

    params = {
        "mes": mes,
        "ano": ano,
        "escola_uuid": escola.uuid,
        "tipo_solicitacao": tipo_solicitacao,
        "eh_lanche_emergencial": eh_lanche_emergencial,
    }
    dias_lanche_emergencial = get_lista_dias_solicitacoes(params, escola)
    dias_lanche_emergencial = list(set(dias_lanche_emergencial))

    valores_da_medicao = (
        ValorMedicao.objects.filter(
            medicao__solicitacao_medicao_inicial=solicitacao,
            nome_campo="lanche_emergencial",
            medicao__grupo__nome="Solicitações de Alimentação",
            dia__in=dias_lanche_emergencial,
        )
        .order_by("dia")
        .exclude(valor=None)
        .values_list("dia", flat=True)
    )
    valores_da_medicao = list(set(valores_da_medicao))
    if len(valores_da_medicao) != len(dias_lanche_emergencial):
        lista_erros.append(
            {
                "periodo_escolar": "Solicitações de Alimentação",
                "erro": "Restam dias a serem lançados nos Lanches Emergenciais.",
            }
        )
    return erros_unicos(lista_erros)


def get_inclusoes_programas_projetos(solicitacao):
    primeiro_dia_mes = datetime.date(int(solicitacao.ano), int(solicitacao.mes), 1)
    ultimo_dia_mes = get_ultimo_dia_mes(primeiro_dia_mes)
    inclusoes = (
        solicitacao.escola.inclusoes_alimentacao_continua.filter(
            status="CODAE_AUTORIZADO",
            data_inicial__lte=ultimo_dia_mes,
            data_final__gte=primeiro_dia_mes,
        )
        .exclude(motivo__nome="ETEC")
        .distinct()
    )
    return inclusoes


def get_inclusoes_etec(solicitacao):
    primeiro_dia_mes = datetime.date(int(solicitacao.ano), int(solicitacao.mes), 1)
    ultimo_dia_mes = get_ultimo_dia_mes(primeiro_dia_mes)
    inclusoes = solicitacao.escola.inclusoes_alimentacao_continua.filter(
        status="CODAE_AUTORIZADO",
        data_inicial__lte=ultimo_dia_mes,
        data_final__gte=primeiro_dia_mes,
        motivo__nome="ETEC",
    ).distinct()
    return inclusoes


def build_nomes_campos_alimentacoes_programas_e_projetos(escola, medicao):
    tipos_alimentacao = list(
        VinculoTipoAlimentacaoComPeriodoEscolarETipoUnidadeEscolar.objects.filter(
            tipo_unidade_escolar=escola.tipo_unidade,
            periodo_escolar__in=escola.periodos_escolares(
                medicao.solicitacao_medicao_inicial.ano
            ),
        )
        .values_list("tipos_alimentacao__nome", flat=True)
        .distinct()
    )

    nomes_campos = ["frequencia"]
    if "Lanche" or "Lanche 4h" in tipos_alimentacao:
        nomes_campos.append("lanche")
    if "Refeição" in tipos_alimentacao:
        nomes_campos.append("refeicao")
        nomes_campos.append("repeticao_refeicao")
    if "Sobremesa" in tipos_alimentacao:
        nomes_campos.append("sobremesa")
        nomes_campos.append("repeticao_sobremesa")
    return nomes_campos


def valida_alimentacoes_solicitacoes_continuas(
    ano, mes, inclusoes, escola, quantidade_dias_mes, medicao_programas_projetos
):
    periodo_com_erro = False
    categoria = CategoriaMedicao.objects.get(nome="ALIMENTAÇÃO")
    nomes_campos = build_nomes_campos_alimentacoes_programas_e_projetos(
        escola, medicao_programas_projetos
    )

    for dia in range(1, quantidade_dias_mes + 1):
        data = datetime.date(year=int(ano), month=int(mes), day=dia)
        dia_semana = data.weekday()
        if (
            periodo_com_erro
            or not inclusoes.filter(
                data_inicial__lte=data,
                data_final__gte=data,
                quantidades_por_periodo__cancelado=False,
                quantidades_por_periodo__dias_semana__icontains=dia_semana,
            ).exists()
            or not escola.calendario.get(data=data).dia_letivo
        ):
            continue
        for nome_campo in nomes_campos:
            if not medicao_programas_projetos.valores_medicao.filter(
                categoria_medicao=categoria,
                nome_campo=nome_campo,
                dia=f"{dia:02d}",
            ).exists():
                periodo_com_erro = True
                continue
    return periodo_com_erro


def get_nomes_campos_categoria(nomes_campos, classificacao, categorias):
    if "ENTERAL" in classificacao.nome or "AMINOÁCIDOS" in classificacao.nome:
        nomes_campos.append("refeicao")
        categoria = categorias.get(nome__icontains="enteral")
    else:
        categoria = categorias.exclude(nome__icontains="enteral").get(
            nome__icontains=classificacao.nome
        )
        try:
            nomes_campos.remove("refeicao")
        except ValueError:
            pass
    return nomes_campos, categoria


def valida_dietas_solicitacoes_continuas(
    escola, mes, ano, quantidade_dias_mes, inclusoes, medicao_programas_projetos
):
    periodo_com_erro_dieta = False

    categorias = CategoriaMedicao.objects.filter(nome__icontains="dieta")
    nomes_campos = ["frequencia", "lanche"]
    ids_categorias_existentes_no_mes = list(
        set(
            escola.logs_dietas_autorizadas.filter(
                data__month=mes, data__year=ano, quantidade__gt=0
            )
            .exclude(classificacao__nome="Tipo C")
            .values_list("classificacao", flat=True)
            .distinct()
        )
    )
    classificacoes = ClassificacaoDieta.objects.filter(
        id__in=ids_categorias_existentes_no_mes
    )
    for classificacao in classificacoes:
        nomes_campos, categoria = get_nomes_campos_categoria(
            nomes_campos, classificacao, categorias
        )
        for dia in range(1, quantidade_dias_mes + 1):
            data = datetime.date(year=int(ano), month=int(mes), day=dia)
            dia_semana = data.weekday()
            if (
                periodo_com_erro_dieta
                or not inclusoes.filter(
                    data_inicial__lte=data,
                    data_final__gte=data,
                    quantidades_por_periodo__cancelado=False,
                    quantidades_por_periodo__dias_semana__icontains=dia_semana,
                ).exists()
                or not escola.calendario.get(data=data).dia_letivo
            ):
                continue
            for nome_campo in nomes_campos:
                if not medicao_programas_projetos.valores_medicao.filter(
                    categoria_medicao=categoria,
                    nome_campo=nome_campo,
                    dia=f"{dia:02d}",
                ).exists():
                    periodo_com_erro_dieta = True
                    continue
    return periodo_com_erro_dieta


def validate_solicitacoes_continuas(
    solicitacao, lista_erros, inclusoes, medicao, nome_secao, valida_dietas
):
    periodo_com_erro_dieta = False
    quantidade_dias_mes = calendar.monthrange(
        int(solicitacao.ano), int(solicitacao.mes)
    )[1]

    periodo_com_erro = valida_alimentacoes_solicitacoes_continuas(
        solicitacao.ano,
        solicitacao.mes,
        inclusoes,
        solicitacao.escola,
        quantidade_dias_mes,
        medicao,
    )
    if valida_dietas:
        periodo_com_erro_dieta = valida_dietas_solicitacoes_continuas(
            solicitacao.escola,
            solicitacao.mes,
            solicitacao.ano,
            quantidade_dias_mes,
            inclusoes,
            medicao,
        )

    if periodo_com_erro_dieta:
        lista_erros.append(
            {
                "periodo_escolar": nome_secao,
                "erro": "Restam dias a serem lançados nas dietas.",
            }
        )

    if periodo_com_erro:
        lista_erros.append(
            {
                "periodo_escolar": nome_secao,
                "erro": "Restam dias a serem lançados nas alimentações.",
            }
        )
    return erros_unicos(lista_erros)


def validate_solicitacoes_programas_e_projetos(solicitacao, lista_erros):
    inclusoes = get_inclusoes_programas_projetos(solicitacao)

    if not inclusoes:
        return lista_erros

    medicao_programas_projetos = solicitacao.get_medicao_programas_e_projetos

    return validate_solicitacoes_continuas(
        solicitacao,
        lista_erros,
        inclusoes,
        medicao_programas_projetos,
        "Programas e Projetos",
        True,
    )


def validate_solicitacoes_etec(solicitacao, lista_erros):
    inclusoes = get_inclusoes_etec(solicitacao)

    if not inclusoes:
        return lista_erros

    medicao_etec = solicitacao.get_medicao_etec

    return validate_solicitacoes_continuas(
        solicitacao, lista_erros, inclusoes, medicao_etec, "ETEC", False
    )
