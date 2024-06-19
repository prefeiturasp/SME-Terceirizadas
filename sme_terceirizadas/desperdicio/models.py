from django.db import models
from ..dados_comuns.behaviors import CriadoEm, TemChaveExterna
from ..cardapio.models import TipoAlimentacao


class ControleSobras(TemChaveExterna, CriadoEm):
    escola = models.ForeignKey('escola.Escola', on_delete=models.DO_NOTHING)
    tipo_alimentacao = models.ForeignKey(TipoAlimentacao, on_delete=models.DO_NOTHING)
    tipo_alimento = models.ForeignKey('produto.TipoAlimento', on_delete=models.DO_NOTHING)
    peso_alimento = models.DecimalField(max_digits=5, decimal_places=2)
    tipo_recipiente = models.ForeignKey('produto.TipoRecipiente', on_delete=models.DO_NOTHING)
    peso_recipiente = models.DecimalField(max_digits=5, decimal_places=2)
    peso_sobra = models.DecimalField(max_digits=5, decimal_places=2)
    usuario = models.ForeignKey('perfil.Usuario', default='', on_delete=models.DO_NOTHING)
    data_medicao = models.DateField('Data da medição', null=True, default=None)
    periodo = models.CharField('Período', max_length=1, blank=True)

    class Meta:
        verbose_name = 'Controle de Sobras'


class ControleRestos(TemChaveExterna, CriadoEm):
    escola = models.ForeignKey('escola.Escola', on_delete=models.DO_NOTHING)
    tipo_alimentacao = models.ForeignKey(TipoAlimentacao, on_delete=models.DO_NOTHING)
    peso_resto = models.DecimalField(max_digits=5, decimal_places=2)
    cardapio = models.CharField('cardapio', max_length=250, blank=True)
    resto_predominante = models.CharField('resto_predominante', max_length=250, blank=True)
    usuario = models.ForeignKey('perfil.Usuario', default='', on_delete=models.DO_NOTHING)
    data_medicao = models.DateField('Data da medição', null=True, default=None)
    quantidade_distribuida = models.DecimalField(max_digits=5, decimal_places=2)
    periodo = models.CharField('Período', max_length=1, blank=True)

    @property
    def imagens(self):
        return self.imagemcontroleresto_set.all()

    class Meta:
        verbose_name = 'Controle de Restos'


class ImagemControleResto(TemChaveExterna):
    controle_resto = models.ForeignKey('ControleRestos', on_delete=models.CASCADE, blank=True)
    arquivo = models.FileField()
    nome = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = 'Imagem do Controle de Resto'
        verbose_name_plural = 'Imagens do Controle de Resto'


class Classificacao(TemChaveExterna, CriadoEm):
    tipo = models.CharField('tipo', max_length=2, blank=True)
    descricao = models.CharField('descricao', max_length=250, blank=True)
    valor = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        verbose_name = 'Classificação'