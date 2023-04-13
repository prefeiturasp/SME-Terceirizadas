
import pytest
from model_mommy import mommy

from sme_terceirizadas.terceirizada.models import Terceirizada


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
def emabalagem_qld():
    return mommy.make('EmbalagemQld', nome='CAIXA', abreviacao='CX')


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
def solicitacao_cronograma_aprovado_dinutre(cronograma):
    return mommy.make(
        'SolicitacaoAlteracaoCronograma',
        numero_solicitacao='00222/2022',
        cronograma=cronograma,
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
def cronograma_assinado_perfil_dinutre(armazem, contrato, empresa):
    return mommy.make(
        'Cronograma',
        numero='003/2022',
        contrato=contrato,
        empresa=empresa,
        armazem=armazem,
        status='ASSINADO_DINUTRE'
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
