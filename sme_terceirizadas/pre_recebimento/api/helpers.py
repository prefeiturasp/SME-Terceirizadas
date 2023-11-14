from sme_terceirizadas.dados_comuns.utils import convert_base64_to_contentfile
from sme_terceirizadas.pre_recebimento.models import (
    ArquivoDoTipoDeDocumento,
    DataDeFabricaoEPrazo,
    EtapasDoCronograma,
    ImagemDoTipoDeEmbalagem,
    ProgramacaoDoRecebimentoDoCronograma,
    TipoDeDocumentoDeRecebimento,
    TipoDeEmbalagemDeLayout
)


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


def cria_tipos_de_embalagens(tipos_de_embalagens, layout_de_embalagem=None):
    for embalagem in tipos_de_embalagens:
        imagens = embalagem.pop('imagens_do_tipo_de_embalagem', [])
        tipo_de_embalagem = TipoDeEmbalagemDeLayout.objects.create(
            layout_de_embalagem=layout_de_embalagem, **embalagem)
        for img in imagens:
            data = convert_base64_to_contentfile(img.get('arquivo'))
            ImagemDoTipoDeEmbalagem.objects.create(
                tipo_de_embalagem=tipo_de_embalagem, arquivo=data, nome=img.get('nome', '')
            )


def cria_tipos_de_documentos(tipos_de_documentos, documento_de_recebimento=None):
    for documento in tipos_de_documentos:
        arquivos = documento.pop('arquivos_do_tipo_de_documento', [])
        tipo_de_documento = TipoDeDocumentoDeRecebimento.objects.create(
            documento_recebimento=documento_de_recebimento, **documento)
        for arq in arquivos:
            data = convert_base64_to_contentfile(arq.get('arquivo'))
            ArquivoDoTipoDeDocumento.objects.create(
                tipo_de_documento=tipo_de_documento, arquivo=data, nome=arq.get('nome', '')
            )


def cria_datas_e_prazos_doc_recebimento(datas_e_prazos, doc_recebimento):
    datas_criadas = []
    for data in datas_e_prazos:
        datas_criadas.append(DataDeFabricaoEPrazo.objects.create(
            documento_recebimento=doc_recebimento,
            **data
        ))
    return datas_criadas
