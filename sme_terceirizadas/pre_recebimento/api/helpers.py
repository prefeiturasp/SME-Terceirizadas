from sme_terceirizadas.pre_recebimento.models import EtapasDoCronograma, ProgramacaoDoRecebimentoDoCronograma


def cria_etapas_de_cronograma(etapas, cronograma=None):
    etapas_criadas = []
    for etapa in etapas:
        etapas_criadas.append(EtapasDoCronograma.objects.create(
            cronograma=cronograma,
            **etapa
        ))
    return etapas_criadas


def cria_programacao_de_cronograma(programacoes, cronograma=None):
    programacoes_criadas = []
    for programacao in programacoes:
        programacoes_criadas.append(ProgramacaoDoRecebimentoDoCronograma.objects.create(
            cronograma=cronograma,
            **programacao
        ))
    return programacoes_criadas
