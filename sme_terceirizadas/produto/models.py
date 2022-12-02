from datetime import datetime

from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from sequences import get_last_value, get_next_value

from ..dados_comuns.behaviors import (
    Ativavel,
    CriadoEm,
    CriadoPor,
    Logs,
    Nomeavel,
    TemAlteradoEm,
    TemChaveExterna,
    TemIdentificadorExternoAmigavel
)
from ..dados_comuns.fluxo_status import (
    FluxoHomologacaoProduto,
    FluxoReclamacaoProduto,
    FluxoSolicitacaoCadastroProduto,
    HomologacaoProdutoWorkflow
)
from ..dados_comuns.models import AnexoLogSolicitacoesUsuario, LogSolicitacoesUsuario, TemplateMensagem
from ..dados_comuns.utils import convert_base64_to_contentfile
from ..escola.models import Escola
from ..terceirizada.models import Edital

MAX_NUMERO_PROTOCOLO = 6


class ProtocoloDeDietaEspecial(Ativavel, CriadoEm, CriadoPor, TemChaveExterna):

    nome = models.CharField('Nome', blank=True, max_length=100, unique=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Protocolo de Dieta Especial'
        verbose_name_plural = 'Protocolos de Dieta Especial'


class Fabricante(Nomeavel, TemChaveExterna):
    item = GenericRelation('ItemCadastro', related_query_name='fabricante')

    def __str__(self):
        return self.nome


class Marca(Nomeavel, TemChaveExterna):
    item = GenericRelation('ItemCadastro', related_query_name='marca')

    def __str__(self):
        return self.nome


class UnidadeMedida(Nomeavel, TemChaveExterna):
    item = GenericRelation('ItemCadastro', related_query_name='unidade_medida')

    def __str__(self):
        return self.nome


class EmbalagemProduto(Nomeavel, TemChaveExterna):
    item = GenericRelation('ItemCadastro', related_query_name='embalagem_produto')

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


class Produto(Ativavel, CriadoEm, CriadoPor, Nomeavel, TemChaveExterna, TemIdentificadorExternoAmigavel):
    eh_para_alunos_com_dieta = models.BooleanField('É para alunos com dieta especial', default=False)

    protocolos = models.ManyToManyField(ProtocoloDeDietaEspecial,
                                        related_name='protocolos',
                                        help_text='Protocolos do produto.',
                                        blank=True,
                                        )

    marca = models.ForeignKey(Marca, on_delete=models.DO_NOTHING, blank=True, null=True)
    fabricante = models.ForeignKey(Fabricante, on_delete=models.DO_NOTHING, blank=True, null=True)
    componentes = models.CharField('Componentes do Produto', blank=True, max_length=5000)

    tem_aditivos_alergenicos = models.BooleanField('Tem aditivos alergênicos', default=False)
    aditivos = models.TextField('Aditivos', blank=True)

    tipo = models.CharField('Tipo do Produto', blank=True, max_length=250)
    embalagem = models.CharField('Embalagem Primária', blank=True, max_length=500)
    prazo_validade = models.CharField('Prazo de validade', blank=True, max_length=100)
    info_armazenamento = models.CharField('Informações de Armazenamento',
                                          blank=True, max_length=500)
    outras_informacoes = models.TextField('Outras Informações', blank=True)
    numero_registro = models.CharField('Registro do órgão competente', blank=True, max_length=100)

    porcao = models.CharField('Porção nutricional', blank=True, max_length=50)
    unidade_caseira = models.CharField('Unidade nutricional', blank=True, max_length=50)
    tem_gluten = models.BooleanField('Tem Glúten?', null=True, default=None)

    @property
    def imagens(self):
        return self.imagemdoproduto_set.all()

    @property
    def informacoes_nutricionais(self):
        return self.informacoes_nutricionais.all()

    @property
    def homologacoes(self):
        try:
            return self.homologacao
        except HomologacaoProduto.DoesNotExist:
            return None

    @property
    def ultima_homologacao(self):
        try:
            return self.homologacao
        except HomologacaoProduto.DoesNotExist:
            return None

    @property
    def data_homologacao(self):
        try:
            homologacao = self.homologacao
            log_homologacao = (
                homologacao.logs
                .filter(status_evento=LogSolicitacoesUsuario.CODAE_HOMOLOGADO)
                .order_by('criado_em')
                .last())
            return log_homologacao.criado_em
        except HomologacaoProduto.DoesNotExist:
            return ''

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


class ProdutoEdital(TemChaveExterna, CriadoEm):

    COMUM = 'Comum'
    DIETA_ESPECIAL = 'Dieta especial'

    TIPO_PRODUTO = {
        COMUM: 'Comum',
        DIETA_ESPECIAL: 'Dieta especial',
    }

    TIPO_PRODUTO_CHOICES = (
        (COMUM, TIPO_PRODUTO[COMUM]),
        (DIETA_ESPECIAL, TIPO_PRODUTO[DIETA_ESPECIAL]),
    )

    produto = models.ForeignKey(Produto, null=False, on_delete=models.DO_NOTHING, related_name='vinculos')
    edital = models.ForeignKey(Edital, null=False, on_delete=models.DO_NOTHING, related_name='vinculos')
    tipo_produto = models.CharField('tipo de produto', max_length=25, choices=TIPO_PRODUTO_CHOICES, null=False, blank=False)  # noqa DJ01
    outras_informacoes = models.TextField('Outras Informações', blank=True)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.produto} -- {self.edital.numero}'

    class Meta:
        verbose_name = 'Vinculo entre produto e edital'
        verbose_name_plural = 'Vinculos entre produtos e editais'
        unique_together = ('produto', 'edital')


class NomeDeProdutoEdital(Ativavel, CriadoEm, CriadoPor, Nomeavel, TemChaveExterna, TemIdentificadorExternoAmigavel):

    class Meta:
        ordering = ('nome',)
        unique_together = ('nome',)
        verbose_name = 'Produto proveniente do Edital'
        verbose_name_plural = 'Produtos provenientes do Edital'

    def __str__(self):
        return self.nome

    def clean(self, *args, **kwargs):
        # Nome sempre em caixa alta.
        self.nome = self.nome.upper()
        return super(NomeDeProdutoEdital, self).clean(*args, **kwargs)


class LogNomeDeProdutoEdital(TemChaveExterna, TemIdentificadorExternoAmigavel, CriadoEm, CriadoPor):
    ACAO = (
        ('a', 'ativar'),
        ('i', 'inativar'),
    )
    acao = models.CharField('ação', max_length=1, choices=ACAO, null=True, blank=True)  # noqa DJ01
    nome_de_produto_edital = models.ForeignKey(
        NomeDeProdutoEdital,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    class Meta:
        ordering = ('-criado_em',)
        verbose_name = 'Log de Produto proveniente do Edital'
        verbose_name_plural = 'Log de Produtos provenientes do Edital'

    def __str__(self):
        return self.id_externo


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


class HomologacaoProduto(TemChaveExterna, CriadoEm, CriadoPor, FluxoHomologacaoProduto,
                         Logs, TemIdentificadorExternoAmigavel, Ativavel):
    DESCRICAO = 'Homologação de Produto'
    produto = models.OneToOneField(Produto, on_delete=models.CASCADE, related_name='homologacao')
    necessita_analise_sensorial = models.BooleanField(default=False)
    protocolo_analise_sensorial = models.CharField(max_length=8, blank=True)
    pdf_gerado = models.BooleanField(default=False)

    @property
    def data_cadastro(self):
        if self.status != self.workflow_class.RASCUNHO:
            log = self.logs.filter(status_evento=LogSolicitacoesUsuario.INICIO_FLUXO).first()
            if log:
                return log.criado_em.date()

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

    @property
    def tempo_aguardando_acao_em_dias(self):
        if self.status in [
            HomologacaoProdutoWorkflow.CODAE_PENDENTE_HOMOLOGACAO,
            HomologacaoProdutoWorkflow.CODAE_QUESTIONADO,
            HomologacaoProdutoWorkflow.CODAE_PEDIU_ANALISE_SENSORIAL,
            HomologacaoProdutoWorkflow.ESCOLA_OU_NUTRICIONISTA_RECLAMOU,
            HomologacaoProdutoWorkflow.CODAE_PEDIU_ANALISE_RECLAMACAO,
            HomologacaoProdutoWorkflow.TERCEIRIZADA_RESPONDEU_RECLAMACAO
        ]:
            intervalo = datetime.today() - self.ultimo_log.criado_em
        else:
            try:
                penultimo_log = self.logs.order_by('-criado_em')[1]
                intervalo = self.ultimo_log.criado_em - penultimo_log.criado_em
            except IndexError:
                intervalo = datetime.today() - self.ultimo_log.criado_em
        return intervalo.days

    @property
    def ultimo_log(self):
        return self.log_mais_recente

    @property
    def ultima_analise(self):
        return self.analises_sensoriais.last()

    def gera_protocolo_analise_sensorial(self):
        id_sequecial = str(get_next_value('protocolo_analise_sensorial'))
        serial = ''
        for _ in range(MAX_NUMERO_PROTOCOLO - len(id_sequecial)):
            serial = serial + '0'
        serial = serial + str(id_sequecial)
        self.protocolo_analise_sensorial = f'AS{serial}'
        self.necessita_analise_sensorial = True
        self.save()

    @classmethod
    def retorna_numero_do_protocolo(cls):
        id_sequecial = get_last_value('protocolo_analise_sensorial')
        serial = ''
        if id_sequecial is None:
            id_sequecial = '1'
        else:
            id_sequecial = str(get_last_value('protocolo_analise_sensorial') + 1)
        for _ in range(MAX_NUMERO_PROTOCOLO - len(id_sequecial)):
            serial = serial + '0'
        serial = serial + str(id_sequecial)
        return f'AS{serial}'

    def salvar_log_transicao(self, status_evento, usuario, **kwargs):
        justificativa = kwargs.get('justificativa', '')
        return LogSolicitacoesUsuario.objects.create(
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


class ReclamacaoDeProduto(FluxoReclamacaoProduto, TemChaveExterna, CriadoEm, CriadoPor,
                          Logs, TemIdentificadorExternoAmigavel):
    homologacao_produto = models.ForeignKey('HomologacaoProduto', on_delete=models.CASCADE,
                                            related_name='reclamacoes', null=True, blank=True)
    reclamante_registro_funcional = models.CharField('RF/CRN/CRF', max_length=50)
    reclamante_cargo = models.CharField('Cargo', max_length=100)
    reclamante_nome = models.CharField('Nome', max_length=255)
    reclamacao = models.TextField('Reclamação')
    escola = models.ForeignKey(Escola, null=True, on_delete=models.PROTECT, related_name='reclamacoes')
    produto_lote = models.TextField(max_length=255, blank=True, default='')
    produto_data_validade = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True)
    produto_data_fabricacao = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True)

    def salvar_log_transicao(self, status_evento, **kwargs):
        justificativa = kwargs.get('justificativa', '')
        user = kwargs['user']
        if user:
            log_transicao = LogSolicitacoesUsuario.objects.create(
                descricao=str(self),
                status_evento=status_evento,
                solicitacao_tipo=LogSolicitacoesUsuario.RECLAMACAO_PRODUTO,
                usuario=user,
                uuid_original=self.uuid,
                justificativa=justificativa
            )
            for anexo in kwargs.get('anexos', []):
                arquivo = convert_base64_to_contentfile(anexo.get('base64'))
                AnexoLogSolicitacoesUsuario.objects.create(
                    log=log_transicao,
                    arquivo=arquivo,
                    nome=anexo['nome']
                )
        return log_transicao

    @property
    def ultimo_log(self):
        return self.log_mais_recente

    def __str__(self):
        return f'Reclamação {self.uuid} feita por {self.reclamante_nome} em {self.criado_em}'


class AnexoReclamacaoDeProduto(TemChaveExterna):
    reclamacao_de_produto = models.ForeignKey(ReclamacaoDeProduto, related_name='anexos', on_delete=models.CASCADE)
    nome = models.CharField(max_length=255, blank=True)
    arquivo = models.FileField()

    def __str__(self):
        return f'Anexo {self.uuid} - {self.nome}'


class RespostaAnaliseSensorial(TemChaveExterna, TemIdentificadorExternoAmigavel, CriadoEm, CriadoPor):
    homologacao_produto = models.ForeignKey('HomologacaoProduto', on_delete=models.CASCADE,
                                            related_name='respostas_analise', null=True, blank=True)
    responsavel_produto = models.CharField(max_length=150)
    registro_funcional = models.CharField(max_length=10)
    data = models.DateField(auto_now=False, auto_now_add=False)
    hora = models.TimeField(auto_now=False, auto_now_add=False)
    observacao = models.TextField(blank=True)

    @property
    def numero_protocolo(self):
        return self.homologacao_de_produto.protocolo_analise_sensorial

    def __str__(self):
        return f'Resposta {self.id_externo} de protocolo {self.numero_protocolo} criada em: {self.criado_em}'


class AnexoRespostaAnaliseSensorial(TemChaveExterna):
    resposta_analise_sensorial = models.ForeignKey(RespostaAnaliseSensorial, related_name='anexos',
                                                   on_delete=models.CASCADE)
    nome = models.CharField(max_length=255, blank=True)
    arquivo = models.FileField()

    def __str__(self):
        return f'Anexo {self.uuid} - {self.nome}'


class SolicitacaoCadastroProdutoDieta(FluxoSolicitacaoCadastroProduto, TemChaveExterna,
                                      TemIdentificadorExternoAmigavel, CriadoEm,
                                      CriadoPor):
    solicitacao_dieta_especial = models.ForeignKey('dieta_especial.SolicitacaoDietaEspecial', on_delete=models.CASCADE,
                                                   related_name='solicitacoes_cadastro_produto')
    aluno = models.ForeignKey('escola.Aluno', on_delete=models.CASCADE,
                              related_name='solicitacoes_cadastro_produto', null=True)
    escola = models.ForeignKey('escola.Escola', on_delete=models.CASCADE,
                               related_name='solicitacoes_cadastro_produto', null=True)
    terceirizada = models.ForeignKey('terceirizada.Terceirizada', on_delete=models.CASCADE,
                                     related_name='solicitacoes_cadastro_produto', null=True)
    nome_produto = models.CharField(max_length=150)
    marca_produto = models.CharField(max_length=150, blank=True)
    fabricante_produto = models.CharField(max_length=150, blank=True)
    info_produto = models.TextField()
    data_previsao_cadastro = models.DateField(null=True)
    justificativa_previsao_cadastro = models.TextField(blank=True)

    def __str__(self):
        return f'Solicitacao cadastro produto {self.nome_produto}'


class AnaliseSensorial(TemChaveExterna, TemIdentificadorExternoAmigavel, CriadoEm):
    # Status Choice
    STATUS_AGUARDANDO_RESPOSTA = 'AGUARDANDO_RESPOSTA'
    STATUS_RESPONDIDA = 'RESPONDIDA'

    STATUS = {
        STATUS_AGUARDANDO_RESPOSTA: 'Aguardando resposta',
        STATUS_RESPONDIDA: 'Respondida',
    }

    STATUS_CHOICES = (
        (STATUS_AGUARDANDO_RESPOSTA, STATUS[STATUS_AGUARDANDO_RESPOSTA]),
        (STATUS_RESPONDIDA, STATUS[STATUS_RESPONDIDA]),
    )

    homologacao_produto = models.ForeignKey('HomologacaoProduto', on_delete=models.CASCADE,
                                            related_name='analises_sensoriais', null=True, blank=True)

    # Terceirizada que irá responder a análise
    terceirizada = models.ForeignKey('terceirizada.Terceirizada', on_delete=models.CASCADE,
                                     related_name='analises_sensoriais', null=True)

    status = models.CharField(
        'Status da análise',
        max_length=25,
        choices=STATUS_CHOICES,
        default=STATUS_AGUARDANDO_RESPOSTA
    )

    @property
    def numero_protocolo(self):
        return self.homologacao_de_produto.protocolo_analise_sensorial

    def __str__(self):
        return f'Análise Sensorial {self.id_externo} de protocolo {self.numero_protocolo} criada em: {self.criado_em}'


class ItemCadastro(TemChaveExterna, CriadoEm):
    """Gerencia Cadastro de itens.

    Permite gerenciar a criação, edição, deleção e consulta
    de modelos que só possuem o atributo nome.

    Exemplos: Marca, Fabricante, Unidade de Medida e Embalagem
    """

    MARCA = 'MARCA'
    FABRICANTE = 'FABRICANTE'
    UNIDADE_MEDIDA = 'UNIDADE_MEDIDA'
    EMBALAGEM = 'EMBALAGEM'

    MODELOS = {
        MARCA: 'Marca',
        FABRICANTE: 'Fabricante',
        UNIDADE_MEDIDA: 'Unidade de Medida',
        EMBALAGEM: 'Embalagem'
    }

    CHOICES = (
        (MARCA, MODELOS[MARCA]),
        (FABRICANTE, MODELOS[FABRICANTE]),
        (UNIDADE_MEDIDA, MODELOS[UNIDADE_MEDIDA]),
        (EMBALAGEM, MODELOS[EMBALAGEM]),
    )

    CLASSES = {MARCA: Marca, FABRICANTE: Fabricante,
               UNIDADE_MEDIDA: UnidadeMedida, EMBALAGEM: EmbalagemProduto}

    tipo = models.CharField(
        'Tipo',
        max_length=30,
        choices=CHOICES
    )

    content_type = models.ForeignKey(ContentType,
                                     on_delete=models.CASCADE)

    object_id = models.PositiveIntegerField()

    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self) -> str:
        return self.content_object.nome

    @classmethod
    def eh_tipo_permitido(cls, tipo: str) -> bool:
        return tipo in [c[0] for c in cls.CHOICES]

    def pode_deletar(self): # noqa C901
        from sme_terceirizadas.produto.models import Produto

        if self.tipo == self.MARCA:
            return not Produto.objects.filter(marca__pk=self.content_object.pk).exists()
        elif self.tipo == self.FABRICANTE:
            return not Produto.objects.filter(fabricante__pk=self.content_object.pk).exists()
        elif self.tipo == self.UNIDADE_MEDIDA:
            return not Produto.objects.filter(especificacoes__unidade_de_medida__pk=self.content_object.pk).exists()
        elif self.tipo == self.EMBALAGEM:
            return not Produto.objects.filter(especificacoes__embalagem_produto__pk=self.content_object.pk).exists()

        return True

    @classmethod
    def criar(cls, nome: str, tipo: str) -> object:
        nome_upper = nome.upper()

        if not cls.eh_tipo_permitido(tipo):
            raise Exception(f'Tipo não permitido: {tipo}')

        modelo = cls.CLASSES[tipo].objects.create(nome=nome_upper)

        item = cls(tipo=tipo, content_object=modelo)
        item.save()
        return item

    @classmethod
    def cria_modelo(cls, nome: str, tipo: str) -> object:
        nome_upper = nome.upper()

        if not cls.eh_tipo_permitido(tipo):
            raise Exception(f'Tipo não permitido: {tipo}')

        modelo = cls.CLASSES[tipo].objects.create(nome=nome_upper)
        return modelo

    def deleta_modelo(self):
        if self.pode_deletar():
            self.content_object.delete()
            self.delete()
            return True

        return False


class EspecificacaoProduto(CriadoEm, TemAlteradoEm, TemChaveExterna):
    """Representa uma especificação de produto.

    Usado na criação do produto e na edição dos rascunhos.
    Ex: Para o produto coca-cola pode-se ter:
    volume: 3, unidade de medida: Litros, embalagem: bag
    volume: 1,5, unidade de medida: Litros, embalagem: bag
    """

    volume = models.FloatField('Volume', null=True)
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name='especificacoes')
    unidade_de_medida = models.ForeignKey(UnidadeMedida, on_delete=models.DO_NOTHING, null=True)
    embalagem_produto = models.ForeignKey(EmbalagemProduto, on_delete=models.DO_NOTHING, null=True)

    class Meta:
        verbose_name = 'Especificicação do Produto'
        verbose_name_plural = 'Especificações do Produto'
