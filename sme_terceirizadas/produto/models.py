from django.db import models

from ..dados_comuns.behaviors import Ativavel, CriadoEm, CriadoPor, Nomeavel, TemChaveExterna


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

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Informação Nutricional'
        verbose_name_plural = 'Informações Nutricionais'


class ImagemDoProduto(TemChaveExterna):
    produto = models.ForeignKey('Produto', on_delete=models.CASCADE)
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
    detalhes_da_dieta = models.TextField()

    marca = models.ForeignKey(Marca, on_delete=models.DO_NOTHING)
    fabricante = models.ForeignKey(Fabricante, on_delete=models.DO_NOTHING)
    componentes = models.CharField('Componentes do Produto', blank=True, max_length=100)

    tem_aditivos_alergenicos = models.BooleanField(default=False)
    aditivos = models.TextField()

    tipo = models.CharField('Tipo do Produto', blank=True, max_length=50)
    embalagem = models.CharField('Embalagem Primária', blank=True, max_length=100)
    prazo_validade = models.CharField('Prazo de validade', blank=True, max_length=100)
    info_armazenamento = models.CharField('Informações de Armazenamento',
                                          blank=True, max_length=100)
    outras_informacoes = models.TextField()
    numero_registro = models.CharField('Registro do órgão competente', blank=True, max_length=100)

    porcao = models.CharField('Porção nutricional', blank=True, max_length=50)
    unidade_caseira = models.CharField('Unidade nutricional', blank=True, max_length=50)

    @property
    def imagens(self):
        return self.imagemdoproduto_set.all()

    @property
    def informacoes_nutricionais(self):
        return self.informacoes_nutricionais.all()

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
    quantidade_porcao = models.CharField('Quantidade por Porção', blank=True, max_length=10)
    valor_diario = models.CharField('%VD(*)', blank=True, max_length=3)

    def __str__(self):
        nome_produto = self.produto.nome
        informacao_nutricional = self.informacao_nutricional.nome
        porcao = self.quantidade_porcao
        valor = self.valor_diario
        return f'{nome_produto} - {informacao_nutricional} => quantidade: {porcao} valor diario: {valor}'

    class Meta:
        verbose_name = 'Informação Nutricional do Produto'
        verbose_name_plural = 'Informações Nutricionais do Produto'
