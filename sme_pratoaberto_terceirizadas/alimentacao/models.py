import uuid as uuid
from django.db import models

from sme_pratoaberto_terceirizadas.food.models import Food
from sme_pratoaberto_terceirizadas.users.models import User


class Gestao(models.Model):
    """ Tipo de Gestão da Refeição"""
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    titulo = models.CharField(verbose_name='Título', max_length=120)
    descricao = models.TextField(verbose_name='Descrição', null=True, blank=True)
    ativo = models.BooleanField(verbose_name='Ativo', default=True)

    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name = 'Gestão'
        verbose_name_plural = 'Gestões'


class Edital(models.Model):
    """ Edital do Cardápio """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    numero = models.CharField(verbose_name='Número', max_length=60)
    descricao = models.TextField(verbose_name='Descrição', null=True, blank=True)
    ativo = models.BooleanField(verbose_name='Ativo', default=True)

    def __str__(self):
        return self.numero

    class Meta:
        verbose_name = 'Edital'
        verbose_name_plural = 'Editais'


class Tipo(models.Model):
    """ Tipo da refeição """

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    codigo = models.CharField(verbose_name='Código', max_length=100,
                              help_text='Ex.: D - DESJEJUM para o título: Desjejum', unique=True)
    titulo = models.CharField(verbose_name='Título', max_length=60)
    descricao = models.TextField(verbose_name='Descrição', null=True, blank=True)
    ativo = models.BooleanField(verbose_name='Ativo', default=True)

    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name = 'Tipo'
        verbose_name_plural = 'Tipos'


class Categoria(models.Model):
    """ Categoria da refeição """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    titulo = models.CharField(verbose_name='Título', max_length=60)
    descricao = models.TextField(verbose_name='Descrição', null=True, blank=True)
    ativo = models.BooleanField(verbose_name='Ativo', default=True)

    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'


class Cardapio(models.Model):
    """ Cardápios """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    data = models.DateField(verbose_name='Data')
    descricao = models.TextField(verbose_name='Descrição', null=True, blank=True)
    criado_por = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='criador')
    criado_em = models.DateTimeField(verbose_name='Criado em', auto_now_add=True)
    atualizado_por = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, blank=True,
                                       related_name='atualizador')
    ultima_atualizacao = models.DateTimeField(verbose_name='Última atualização', auto_now=True)
    edital = models.ForeignKey(Edital, on_delete=models.DO_NOTHING)
    tipo = models.ForeignKey(Tipo, on_delete=models.DO_NOTHING, help_text='Ex: Café, Almoço e Janta')
    categoria = models.ForeignKey(Categoria, on_delete=models.DO_NOTHING, help_text='Ex: Lactante, Normal ou Diabética')
    alimento = models.ManyToManyField(Food)

    def __str__(self):
        return '{} - {}'.format(self.data, self.descricao)
