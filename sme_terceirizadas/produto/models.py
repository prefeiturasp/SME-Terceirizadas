from django.db import models

from ..dados_comuns.behaviors import (
    Ativavel,
    CriadoEm,
    CriadoPor,
    Logs,
    Nomeavel,
    TemChaveExterna,
    TemIdentificadorExternoAmigavel
)
from ..dados_comuns.fluxo_status import FluxoHomologacaoProduto
from ..dados_comuns.models import LogSolicitacoesUsuario, TemplateMensagem


class ProtocoloDeDietaEspecial(Ativavel, CriadoEm, CriadoPor, Nomeavel, TemChaveExterna):

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Protocolo de Dieta Especial'
        verbose_name_plural = 'Protocolos de Dieta Especial'


class Fabricante(Nomeavel, TemChaveExterna):

    def __str__(self):
        return self.nome


class Marca(Nomeavel, TemChaveExterna):

    def __str__(self):
        return self.nome


class TipoDeInformacaoNutricional(Nomeavel, TemChaveExterna):
    def __str__(self):
        return self.nome


class InformacaoNutricional(TemChaveExterna, Nomeavel):
    tipo_nutricional = models.ForeignKey(TipoDeInformacaoNutricional, on_delete=models.DO_NOTHING)
    medida = models.CharField(max_length=10, blank=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Informação Nutricional'
        verbose_name_plural = 'Informações Nutricionais'


class ImagemDoProduto(TemChaveExterna):
    produto = models.ForeignKey('Produto', on_delete=models.CASCADE, blank=True)
    arquivo = models.FileField()
    nome = models.CharField(max_length=100, blank=True)

    class Meta:
        verbose_name = 'Imagem do Produto'
        verbose_name_plural = 'Imagens do Produto'


class Produto(Ativavel, CriadoEm, CriadoPor, Nomeavel, TemChaveExterna):
    eh_para_alunos_com_dieta = models.BooleanField(default=False)
    protocolos = models.ManyToManyField(ProtocoloDeDietaEspecial,
                                        related_name='protocolos',
                                        help_text='Protocolos do produto.',
                                        blank=True,
                                        )

    marca = models.ForeignKey(Marca, on_delete=models.DO_NOTHING)
    fabricante = models.ForeignKey(Fabricante, on_delete=models.DO_NOTHING)
    componentes = models.CharField('Componentes do Produto', blank=True, max_length=500)

    tem_aditivos_alergenicos = models.BooleanField(default=False)
    aditivos = models.TextField(blank=True)

    tipo = models.CharField('Tipo do Produto', blank=True, max_length=250)
    embalagem = models.CharField('Embalagem Primária', blank=True, max_length=100)
    prazo_validade = models.CharField('Prazo de validade', blank=True, max_length=100)
    info_armazenamento = models.CharField('Informações de Armazenamento',
                                          blank=True, max_length=500)
    outras_informacoes = models.TextField(blank=True)
    numero_registro = models.CharField('Registro do órgão competente', blank=True, max_length=100)

    porcao = models.CharField('Porção nutricional', blank=True, max_length=50)
    unidade_caseira = models.CharField('Unidade nutricional', blank=True, max_length=50)

    @property
    def imagens(self):
        return self.imagemdoproduto_set.all()

    @property
    def informacoes_nutricionais(self):
        return self.informacoes_nutricionais.all()

    @property
    def homologacoes(self):
        return self.homologacoes.all()

    @classmethod
    def filtrar_por_nome(cls, **kwargs):
        nome = kwargs.get('nome')
        return cls.objects.filter(nome__icontains=nome)

    @classmethod
    def filtrar_por_marca(cls, **kwargs):
        nome = kwargs.get('nome')
        return cls.objects.filter(marca__nome__icontains=nome)

    @classmethod
    def filtrar_por_fabricante(cls, **kwargs):
        nome = kwargs.get('nome')
        return cls.objects.filter(fabricante__nome__icontains=nome)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'


class InformacoesNutricionaisDoProduto(TemChaveExterna):
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name='informacoes_nutricionais')
    informacao_nutricional = models.ForeignKey(InformacaoNutricional, on_delete=models.DO_NOTHING)
    quantidade_porcao = models.CharField(max_length=10)
    valor_diario = models.CharField(max_length=10)

    def __str__(self):
        nome_produto = self.produto.nome
        informacao_nutricional = self.informacao_nutricional.nome
        porcao = self.quantidade_porcao
        valor = self.valor_diario
        return f'{nome_produto} - {informacao_nutricional} => quantidade: {porcao} valor diario: {valor}'

    class Meta:
        verbose_name = 'Informação Nutricional do Produto'
        verbose_name_plural = 'Informações Nutricionais do Produto'


class HomologacaoDoProduto(TemChaveExterna, CriadoEm, CriadoPor, FluxoHomologacaoProduto,
                           Logs, TemIdentificadorExternoAmigavel, Ativavel):
    DESCRICAO = 'Homologação de Produto'
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name='homologacoes')
    necessita_analise_sensorial = models.BooleanField(default=False)

    @property
    def template_mensagem(self):
        template = TemplateMensagem.objects.get(tipo=TemplateMensagem.HOMOLOGACAO_PRODUTO)
        template_troca = {
            '@id': self.id_externo,
            '@criado_em': str(self.criado_em),
            '@criado_por': str(self.criado_por),
            '@status': str(self.status),
            # TODO: verificar a url padrão do pedido
            '@link': 'http://teste.com',
        }
        corpo = template.template_html
        for chave, valor in template_troca.items():
            corpo = corpo.replace(chave, valor)
        return template.assunto, corpo

    def salvar_log_transicao(self, status_evento, usuario, **kwargs):
        justificativa = kwargs.get('justificativa', '')
        LogSolicitacoesUsuario.objects.create(
            descricao=str(self),
            status_evento=status_evento,
            solicitacao_tipo=LogSolicitacoesUsuario.HOMOLOGACAO_PRODUTO,
            usuario=usuario,
            uuid_original=self.uuid,
            justificativa=justificativa
        )

    class Meta:
        ordering = ('-ativo', '-criado_em')
        verbose_name = 'Homologação de Produto'
        verbose_name_plural = 'Homologações de Produto'

    def __str__(self):
        return f'Homologação #{self.id_externo}'
