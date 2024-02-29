from sme_terceirizadas.dados_comuns.utils import (
    convert_base64_to_contentfile,
    update_instance_from_dict,
)
from sme_terceirizadas.pre_recebimento.models import (
    AnaliseFichaTecnica,
    ArquivoDoTipoDeDocumento,
    DataDeFabricaoEPrazo,
    EtapasDoCronograma,
    FichaTecnicaDoProduto,
    ImagemDoTipoDeEmbalagem,
    InformacoesNutricionaisFichaTecnica,
    ProgramacaoDoRecebimentoDoCronograma,
    TipoDeDocumentoDeRecebimento,
    TipoDeEmbalagemDeLayout,
)
from sme_terceirizadas.produto.models import InformacaoNutricional


def cria_etapas_de_cronograma(etapas, cronograma=None):
    etapas_criadas = []
    for etapa in etapas:
        etapas_criadas.append(
            EtapasDoCronograma.objects.create(cronograma=cronograma, **etapa)
        )
    return etapas_criadas


def cria_programacao_de_cronograma(programacoes, cronograma=None):
    programacoes_criadas = []
    for programacao in programacoes:
        programacoes_criadas.append(
            ProgramacaoDoRecebimentoDoCronograma.objects.create(
                cronograma=cronograma, **programacao
            )
        )
    return programacoes_criadas


def cria_tipos_de_embalagens(tipos_de_embalagens, layout_de_embalagem=None):
    for embalagem in tipos_de_embalagens:
        imagens = embalagem.pop("imagens_do_tipo_de_embalagem", [])
        tipo_de_embalagem = TipoDeEmbalagemDeLayout.objects.create(
            layout_de_embalagem=layout_de_embalagem, **embalagem
        )
        for img in imagens:
            data = convert_base64_to_contentfile(img.get("arquivo"))
            ImagemDoTipoDeEmbalagem.objects.create(
                tipo_de_embalagem=tipo_de_embalagem,
                arquivo=data,
                nome=img.get("nome", ""),
            )


def cria_tipos_de_documentos(tipos_de_documentos, documento_de_recebimento=None):
    for documento in tipos_de_documentos:
        arquivos = documento.pop("arquivos_do_tipo_de_documento", [])
        tipo_de_documento = TipoDeDocumentoDeRecebimento.objects.create(
            documento_recebimento=documento_de_recebimento, **documento
        )
        for arq in arquivos:
            data = convert_base64_to_contentfile(arq.get("arquivo"))
            ArquivoDoTipoDeDocumento.objects.create(
                tipo_de_documento=tipo_de_documento,
                arquivo=data,
                nome=arq.get("nome", ""),
            )


def cria_datas_e_prazos_doc_recebimento(datas_e_prazos, doc_recebimento):
    datas_criadas = []
    for data in datas_e_prazos:
        datas_criadas.append(
            DataDeFabricaoEPrazo.objects.create(
                documento_recebimento=doc_recebimento, **data
            )
        )
    return datas_criadas


def cria_ficha_tecnica(validated_data):
    dados_informacoes_nutricionais = validated_data.pop("informacoes_nutricionais", [])

    _converte_arquivo_para_contentfile(validated_data)

    instance = FichaTecnicaDoProduto.objects.create(**validated_data)

    if dados_informacoes_nutricionais:
        _cria_informacoes_nutricionais(
            instance,
            dados_informacoes_nutricionais,
        )

    return instance


def atualiza_ficha_tecnica(instance, validated_data):
    dados_informacoes_nutricionais = validated_data.pop("informacoes_nutricionais", [])

    _converte_arquivo_para_contentfile(validated_data)

    if dados_informacoes_nutricionais:
        _cria_informacoes_nutricionais(
            instance,
            dados_informacoes_nutricionais,
            deletar_antigas=True,
        )

    return update_instance_from_dict(instance, validated_data, save=True)


def _converte_arquivo_para_contentfile(validated_data):
    arquivo_base64 = validated_data.pop("arquivo", None)
    if arquivo_base64:
        validated_data["arquivo"] = convert_base64_to_contentfile(arquivo_base64)


def _cria_informacoes_nutricionais(
    ficha_tecnica,
    dados_informacoes_nutricionais,
    deletar_antigas=False,
):
    if deletar_antigas:
        ficha_tecnica.informacoes_nutricionais.all().delete()

    for dados in dados_informacoes_nutricionais:
        informacao_nutricional = InformacaoNutricional.objects.filter(
            uuid=str(dados["informacao_nutricional"])
        ).first()

        InformacoesNutricionaisFichaTecnica.objects.create(
            ficha_tecnica=ficha_tecnica,
            informacao_nutricional=informacao_nutricional,
            quantidade_por_100g=dados["quantidade_por_100g"],
            quantidade_porcao=dados["quantidade_porcao"],
            valor_diario=dados["valor_diario"],
        )


def limpar_campos_dependentes_ficha_tecnica(instance, validated_data):
    if validated_data.get("organico") is False:
        setattr(instance, "mecanismo_controle", None)

    if validated_data.get("alergenicos") is False:
        setattr(instance, "ingredientes_alergenicos", None)

    if validated_data.get("lactose") is False:
        setattr(instance, "lactose_detalhe", None)

    if validated_data.get("produto_eh_liquido") is False:
        setattr(instance, "volume_embalagem_primaria", None)
        setattr(instance, "unidade_medida_volume_primaria", None)

    return instance


def gerar_nova_analise_ficha_tecnica(ficha_tecnica):
    campos_conferidos = [
        campo.name
        for campo in AnaliseFichaTecnica._meta.fields
        if campo.name.endswith("_conferido")
    ]

    analise_antiga = ficha_tecnica.analises.last()

    valores_conferidos_antigos = {
        campo: getattr(analise_antiga, campo)
        for campo in campos_conferidos
        if getattr(analise_antiga, campo) is True
    }

    AnaliseFichaTecnica.objects.create(
        criado_por=analise_antiga.criado_por,
        ficha_tecnica=ficha_tecnica,
        **valores_conferidos_antigos,
    )
