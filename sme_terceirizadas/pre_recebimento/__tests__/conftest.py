import pytest
from model_mommy import mommy

from sme_terceirizadas.dados_comuns.fluxo_status import LayoutDeEmbalagemWorkflow
from sme_terceirizadas.dados_comuns.models import LogSolicitacoesUsuario
from sme_terceirizadas.terceirizada.models import Terceirizada

from ..models import LayoutDeEmbalagem, TipoDeEmbalagemDeLayout, UnidadeMedida


@pytest.fixture
def contrato():
    return mommy.make('Contrato',
                      numero='0003/2022',
                      processo='123')


@pytest.fixture
def empresa(contrato):
    return mommy.make('Terceirizada',
                      nome_fantasia='Alimentos SA',
                      razao_social='Alimentos',
                      contratos=[contrato],
                      tipo_servico=Terceirizada.FORNECEDOR,
                      )


@pytest.fixture
def cronograma():
    return mommy.make('Cronograma', numero='001/2022')


@pytest.fixture
def cronograma_rascunho(armazem, contrato, empresa):
    return mommy.make(
        'Cronograma',
        numero='002/2022',
        contrato=contrato,
        armazem=armazem,
        empresa=empresa,
    )


@pytest.fixture
def cronograma_recebido(armazem, contrato, empresa):
    return mommy.make(
        'Cronograma',
        numero='002/2022',
        contrato=contrato,
        empresa=empresa,
        armazem=armazem,
        status='ASSINADO_E_ENVIADO_AO_FORNECEDOR'
    )


@pytest.fixture
def etapa(cronograma):
    return mommy.make('EtapasDoCronograma', cronograma=cronograma, etapa='Etapa 1')


@pytest.fixture
def programacao(cronograma):
    return mommy.make('ProgramacaoDoRecebimentoDoCronograma', cronograma=cronograma, data_programada='01/01/2022')


@pytest.fixture
def armazem():
    return mommy.make(Terceirizada,
                      nome_fantasia='Alimentos SA',
                      tipo_servico=Terceirizada.DISTRIBUIDOR_ARMAZEM,
                      )


@pytest.fixture
def laboratorio():
    return mommy.make('Laboratorio', nome='Labo Test')


@pytest.fixture
def tipo_emabalagem_qld():
    return mommy.make('TipoEmbalagemQld', nome='CAIXA', abreviacao='CX')


@pytest.fixture
def cronograma_solicitado_alteracao(armazem, contrato, empresa):
    return mommy.make(
        'Cronograma',
        numero='00222/2022',
        contrato=contrato,
        empresa=empresa,
        armazem=armazem,
        status='SOLICITADO_ALTERACAO'
    )


@pytest.fixture
def solicitacao_cronograma_em_analise(cronograma):
    return mommy.make(
        'SolicitacaoAlteracaoCronograma',
        numero_solicitacao='00222/2022',
        cronograma=cronograma,
        status='EM_ANALISE'
    )


@pytest.fixture
def solicitacao_cronograma_ciente(cronograma):
    return mommy.make(
        'SolicitacaoAlteracaoCronograma',
        numero_solicitacao='00222/2022',
        cronograma=cronograma,
        status='CRONOGRAMA_CIENTE'
    )


@pytest.fixture
def solicitacao_cronograma_aprovado_dinutre(cronograma_solicitado_alteracao):
    return mommy.make(
        'SolicitacaoAlteracaoCronograma',
        numero_solicitacao='00222/2022',
        cronograma=cronograma_solicitado_alteracao,
        status='APROVADO_DINUTRE'
    )


@pytest.fixture
def cronograma_assinado_fornecedor(armazem, contrato, empresa):
    return mommy.make(
        'Cronograma',
        numero='002/2022',
        contrato=contrato,
        empresa=empresa,
        armazem=armazem,
        status='ASSINADO_FORNECEDOR'
    )


@pytest.fixture
def cronograma_assinado_perfil_cronograma(armazem, contrato, empresa):
    return mommy.make(
        'Cronograma',
        numero='002/2022',
        contrato=contrato,
        empresa=empresa,
        armazem=armazem,
        status='ASSINADO_E_ENVIADO_AO_FORNECEDOR'
    )


@pytest.fixture
def cronograma_assinado_perfil_dinutre(armazem, contrato, empresa, produto_arroz):
    return mommy.make(
        'Cronograma',
        numero='003/2022',
        contrato=contrato,
        empresa=empresa,
        armazem=armazem,
        produto=produto_arroz,
        status='ASSINADO_DINUTRE'
    )


@pytest.fixture
def cronograma_assinado_perfil_dilog(armazem, contrato, empresa, produto_macarrao):
    return mommy.make(
        'Cronograma',
        numero='004/2022',
        contrato=contrato,
        empresa=empresa,
        armazem=armazem,
        produto=produto_macarrao,
        status='ASSINADO_CODAE'
    )


@pytest.fixture
def produto_arroz():
    return mommy.make('NomeDeProdutoEdital', nome='Arroz')


@pytest.fixture
def produto_macarrao():
    return mommy.make('NomeDeProdutoEdital', nome='Macarrão')


@pytest.fixture
def produto_feijao():
    return mommy.make('NomeDeProdutoEdital', nome='Feijão')


@pytest.fixture
def produto_acucar():
    return mommy.make('NomeDeProdutoEdital', nome='Açucar')


@pytest.fixture
def cronogramas_multiplos_status_com_log(armazem, contrato, empresa, produto_arroz, produto_macarrao, produto_feijao,
                                         produto_acucar):
    c1 = mommy.make('Cronograma',
                    numero='002/2023', contrato=contrato, empresa=empresa, armazem=armazem, produto=produto_arroz,
                    status='ASSINADO_FORNECEDOR'
                    )
    c2 = mommy.make('Cronograma',
                    numero='003/2023', contrato=contrato, empresa=empresa, armazem=armazem, produto=produto_acucar,
                    status='ASSINADO_FORNECEDOR'
                    )
    c3 = mommy.make('Cronograma',
                    numero='004/2023', contrato=contrato, empresa=empresa, armazem=armazem, produto=produto_arroz,
                    status='ASSINADO_DINUTRE'
                    )
    c4 = mommy.make('Cronograma',
                    numero='005/2023', contrato=contrato, empresa=empresa, armazem=armazem, produto=produto_feijao,
                    status='ASSINADO_DINUTRE'
                    )
    c5 = mommy.make('Cronograma',
                    numero='006/2023', contrato=contrato, empresa=empresa, armazem=armazem, produto=produto_macarrao,
                    status='ASSINADO_FORNECEDOR'
                    )
    c6 = mommy.make('Cronograma',
                    numero='007/2023', contrato=contrato, empresa=empresa, armazem=armazem, produto=produto_macarrao,
                    status='ASSINADO_CODAE'
                    )
    mommy.make('LogSolicitacoesUsuario',
               uuid_original=c1.uuid,
               status_evento=59,  # CRONOGRAMA_ASSINADO_PELO_USUARIO_CRONOGRAMA
               solicitacao_tipo=19)  # CRONOGRAMA
    mommy.make('LogSolicitacoesUsuario',
               uuid_original=c2.uuid,
               status_evento=59,  # CRONOGRAMA_ASSINADO_PELO_USUARIO_CRONOGRAMA
               solicitacao_tipo=19)  # CRONOGRAMA
    mommy.make('LogSolicitacoesUsuario',
               uuid_original=c3.uuid,
               status_evento=69,  # CRONOGRAMA_ASSINADO_PELA_DINUTRE
               solicitacao_tipo=19)  # CRONOGRAMA
    mommy.make('LogSolicitacoesUsuario',
               uuid_original=c4.uuid,
               status_evento=69,  # CRONOGRAMA_ASSINADO_PELA_DINUTRE
               solicitacao_tipo=19)  # CRONOGRAMA
    mommy.make('LogSolicitacoesUsuario',
               uuid_original=c5.uuid,
               status_evento=59,  # CRONOGRAMA_ASSINADO_PELO_USUARIO_CRONOGRAMA
               solicitacao_tipo=19)  # CRONOGRAMA
    mommy.make('LogSolicitacoesUsuario',
               uuid_original=c6.uuid,
               status_evento=70,  # CRONOGRAMA_ASSINADO_PELA_CODAE
               solicitacao_tipo=19)  # CRONOGRAMA


@pytest.fixture
def cronogramas_multiplos_status_com_log_cronograma_ciente(armazem, contrato, empresa,
                                                           produto_arroz, produto_acucar):
    c1 = mommy.make('Cronograma',
                    numero='002/2023', contrato=contrato, empresa=empresa, armazem=armazem, produto=produto_arroz,
                    status='SOLICITADO_ALTERACAO'
                    )
    c2 = mommy.make('Cronograma',
                    numero='003/2023', contrato=contrato, empresa=empresa, armazem=armazem, produto=produto_acucar,
                    status='SOLICITADO_ALTERACAO'
                    )
    s1 = mommy.make(
        'SolicitacaoAlteracaoCronograma',
        numero_solicitacao='00222/2022',
        cronograma=c1,
        status='CRONOGRAMA_CIENTE'
    )
    s2 = mommy.make(
        'SolicitacaoAlteracaoCronograma',
        numero_solicitacao='00223/2022',
        cronograma=c2,
        status='CRONOGRAMA_CIENTE'
    )
    mommy.make('LogSolicitacoesUsuario',
               uuid_original=s1.uuid,
               status_evento=71,  # CRONOGRAMA_CIENTE_SOLICITACAO_ALTERACAO
               solicitacao_tipo=20)  # CRONOGRAMA
    mommy.make('LogSolicitacoesUsuario',
               uuid_original=s2.uuid,
               status_evento=71,  # CRONOGRAMA_CIENTE_SOLICITACAO_ALTERACAO
               solicitacao_tipo=20)  # CRONOGRAMA
    mommy.make('LogSolicitacoesUsuario',
               uuid_original=c1.uuid,
               status_evento=71,  # CRONOGRAMA_CIENTE_SOLICITACAO_ALTERACAO
               solicitacao_tipo=19)  # CRONOGRAMA
    mommy.make('LogSolicitacoesUsuario',
               uuid_original=c2.uuid,
               status_evento=71,  # CRONOGRAMA_CIENTE_SOLICITACAO_ALTERACAO
               solicitacao_tipo=19)  # CRONOGRAMA


@pytest.fixture
def unidade_medida_logistica():
    return mommy.make(UnidadeMedida, nome='UNIDADE TESTE', abreviacao='ut')


@pytest.fixture
def unidades_medida_logistica():
    data = [
        {'nome': f'UNIDADE TESTE {i}', 'abreviacao': f'ut{i}'}
        for i in range(1, 21)
    ]
    objects = [mommy.make(UnidadeMedida, **attrs) for attrs in data]
    return objects


@pytest.fixture
def unidades_medida_reais_logistica():
    data = [
        {'nome': 'KILOGRAMA', 'abreviacao': 'kg'},
        {'nome': 'LITRO', 'abreviacao': 'l'}
    ]
    objects = [mommy.make(UnidadeMedida, **attrs) for attrs in data]
    return objects


@pytest.fixture
def layout_de_embalagem(cronograma_assinado_perfil_dilog):
    return mommy.make('LayoutDeEmbalagem',
                      cronograma=cronograma_assinado_perfil_dilog,
                      observacoes='teste')


@pytest.fixture
def tipo_de_embalagem_de_layout(layout_de_embalagem):
    return mommy.make('TipoDeEmbalagemDeLayout',
                      layout_de_embalagem=layout_de_embalagem,
                      tipo_embalagem='PRIMARIA',
                      status='APROVADO',
                      complemento_do_status='Teste de aprovacao')


@pytest.fixture
def arquivo_base64():
    arquivo = f'data:image/jpeg;base64,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' # noqa
    return arquivo


@pytest.fixture
def lista_layouts_de_embalagem_enviados_para_analise(
    cronograma_assinado_perfil_dinutre,
    cronograma_assinado_perfil_dilog
):
    layouts_cronograma_assinado_dinutre = [
        {
            'cronograma': cronograma_assinado_perfil_dinutre,
            'observacoes': f'Teste {i}',
            'status': LayoutDeEmbalagemWorkflow.ENVIADO_PARA_ANALISE
        }
        for i in range(1, 6)
    ]

    layouts_cronograma_assinado_dilog = [
        {
            'cronograma': cronograma_assinado_perfil_dilog,
            'observacoes': f'Teste {i}',
            'status': LayoutDeEmbalagemWorkflow.ENVIADO_PARA_ANALISE
        }
        for i in range(6, 16)
    ]

    data = layouts_cronograma_assinado_dilog + layouts_cronograma_assinado_dinutre

    objects = [mommy.make(LayoutDeEmbalagem, **attrs) for attrs in data]

    return objects


@pytest.fixture
def lista_layouts_de_embalagem_aprovados(
    cronograma_assinado_perfil_dinutre,
    cronograma_assinado_perfil_dilog
):
    layouts_cronograma_assinado_dinutre = [
        {
            'cronograma': cronograma_assinado_perfil_dinutre,
            'observacoes': f'Teste {i}',
            'status': LayoutDeEmbalagemWorkflow.APROVADO
        }
        for i in range(1, 6)
    ]

    layouts_cronograma_assinado_dilog = [
        {
            'cronograma': cronograma_assinado_perfil_dilog,
            'observacoes': f'Teste {i}',
            'status': LayoutDeEmbalagemWorkflow.APROVADO
        }
        for i in range(6, 16)
    ]

    data = layouts_cronograma_assinado_dilog + layouts_cronograma_assinado_dinutre

    objects = [mommy.make(LayoutDeEmbalagem, **attrs) for attrs in data]

    return objects


@pytest.fixture
def lista_layouts_de_embalagem_solicitado_correcao(
    cronograma_assinado_perfil_dinutre,
    cronograma_assinado_perfil_dilog
):
    layouts_cronograma_assinado_dinutre = [
        {
            'cronograma': cronograma_assinado_perfil_dinutre,
            'observacoes': f'Teste {i}',
            'status': LayoutDeEmbalagemWorkflow.SOLICITADO_CORRECAO
        }
        for i in range(1, 6)
    ]

    layouts_cronograma_assinado_dilog = [
        {
            'cronograma': cronograma_assinado_perfil_dilog,
            'observacoes': f'Teste {i}',
            'status': LayoutDeEmbalagemWorkflow.SOLICITADO_CORRECAO
        }
        for i in range(6, 16)
    ]

    data = layouts_cronograma_assinado_dilog + layouts_cronograma_assinado_dinutre

    objects = [mommy.make(LayoutDeEmbalagem, **attrs) for attrs in data]

    return objects


@pytest.fixture
def lista_layouts_de_embalagem_com_tipo_embalagem(cronograma_assinado_perfil_dilog):
    dados_layouts = [
        {
            'cronograma': cronograma_assinado_perfil_dilog,
            'observacoes': f'Teste {i}',
            'status': LayoutDeEmbalagemWorkflow.ENVIADO_PARA_ANALISE
        }
        for i in range(1, 3)
    ]

    layouts = [mommy.make(LayoutDeEmbalagem, **attrs) for attrs in dados_layouts]

    mommy.make(
        TipoDeEmbalagemDeLayout,
        layout_de_embalagem=layouts[0],
        tipo_embalagem=TipoDeEmbalagemDeLayout.TIPO_EMBALAGEM_PRIMARIA
    )
    mommy.make(
        TipoDeEmbalagemDeLayout,
        layout_de_embalagem=layouts[0],
        tipo_embalagem=TipoDeEmbalagemDeLayout.TIPO_EMBALAGEM_SECUNDARIA
    )
    mommy.make(
        TipoDeEmbalagemDeLayout,
        layout_de_embalagem=layouts[0],
        tipo_embalagem=TipoDeEmbalagemDeLayout.TIPO_EMBALAGEM_TERCIARIA
    )

    mommy.make(
        TipoDeEmbalagemDeLayout,
        layout_de_embalagem=layouts[1],
        tipo_embalagem=TipoDeEmbalagemDeLayout.TIPO_EMBALAGEM_PRIMARIA
    )
    mommy.make(
        TipoDeEmbalagemDeLayout,
        layout_de_embalagem=layouts[1],
        tipo_embalagem=TipoDeEmbalagemDeLayout.TIPO_EMBALAGEM_SECUNDARIA
    )

    return layouts


@pytest.fixture
def lista_layouts_de_embalagem(
    lista_layouts_de_embalagem_enviados_para_analise,
    lista_layouts_de_embalagem_aprovados,
    lista_layouts_de_embalagem_solicitado_correcao
):
    return (
        lista_layouts_de_embalagem_enviados_para_analise +
        lista_layouts_de_embalagem_aprovados +
        lista_layouts_de_embalagem_solicitado_correcao
    )


@pytest.fixture
def layout_de_embalagem_para_correcao(cronograma_assinado_perfil_dilog, arquivo_base64):
    layout = mommy.make(
        LayoutDeEmbalagem,
        cronograma=cronograma_assinado_perfil_dilog,
        observacoes='Imagine uma observação aqui.',
        status=LayoutDeEmbalagemWorkflow.SOLICITADO_CORRECAO
    )
    mommy.make(
        TipoDeEmbalagemDeLayout,
        layout_de_embalagem=layout,
        tipo_embalagem=TipoDeEmbalagemDeLayout.TIPO_EMBALAGEM_PRIMARIA,
        status=TipoDeEmbalagemDeLayout.STATUS_REPROVADO
    )
    mommy.make(
        TipoDeEmbalagemDeLayout,
        layout_de_embalagem=layout,
        tipo_embalagem=TipoDeEmbalagemDeLayout.TIPO_EMBALAGEM_SECUNDARIA,
        status=TipoDeEmbalagemDeLayout.STATUS_APROVADO
    )

    return layout


@pytest.fixture
def layout_de_embalagem_aprovado(cronograma_assinado_perfil_dilog, arquivo_base64):
    layout = mommy.make(
        LayoutDeEmbalagem,
        cronograma=cronograma_assinado_perfil_dilog,
        observacoes='Imagine uma observação aqui.',
        status=LayoutDeEmbalagemWorkflow.APROVADO
    )
    mommy.make(
        TipoDeEmbalagemDeLayout,
        layout_de_embalagem=layout,
        tipo_embalagem=TipoDeEmbalagemDeLayout.TIPO_EMBALAGEM_PRIMARIA,
        status=TipoDeEmbalagemDeLayout.STATUS_APROVADO
    )
    mommy.make(
        TipoDeEmbalagemDeLayout,
        layout_de_embalagem=layout,
        tipo_embalagem=TipoDeEmbalagemDeLayout.TIPO_EMBALAGEM_SECUNDARIA,
        status=TipoDeEmbalagemDeLayout.STATUS_APROVADO
    )

    return layout


@pytest.fixture
def layout_de_embalagem_em_analise_com_correcao(cronograma_assinado_perfil_dilog, arquivo_base64):
    layout = mommy.make(
        LayoutDeEmbalagem,
        cronograma=cronograma_assinado_perfil_dilog,
        observacoes='Imagine uma observação aqui.',
        status=LayoutDeEmbalagemWorkflow.ENVIADO_PARA_ANALISE
    )
    mommy.make(
        TipoDeEmbalagemDeLayout,
        layout_de_embalagem=layout,
        tipo_embalagem=TipoDeEmbalagemDeLayout.TIPO_EMBALAGEM_PRIMARIA,
        status=TipoDeEmbalagemDeLayout.STATUS_EM_ANALISE
    )
    mommy.make(
        TipoDeEmbalagemDeLayout,
        layout_de_embalagem=layout,
        tipo_embalagem=TipoDeEmbalagemDeLayout.TIPO_EMBALAGEM_SECUNDARIA,
        status=TipoDeEmbalagemDeLayout.STATUS_APROVADO
    )
    mommy.make(
        TipoDeEmbalagemDeLayout,
        layout_de_embalagem=layout,
        tipo_embalagem=TipoDeEmbalagemDeLayout.TIPO_EMBALAGEM_TERCIARIA,
        status=TipoDeEmbalagemDeLayout.STATUS_EM_ANALISE
    )
    mommy.make(LogSolicitacoesUsuario,
               uuid_original=layout.uuid,
               status_evento=LogSolicitacoesUsuario.LAYOUT_CORRECAO_REALIZADA,
               solicitacao_tipo=LogSolicitacoesUsuario.LAYOUT_DE_EMBALAGEM)

    return layout
