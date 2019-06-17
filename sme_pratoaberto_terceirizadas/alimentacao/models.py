import uuid as uuid
from enum import Enum
from django.utils.timezone import now

from django.db import models

from sme_pratoaberto_terceirizadas.food.models import Alimento
from sme_pratoaberto_terceirizadas.escola.models import Escola
from sme_pratoaberto_terceirizadas.users.models import User
from .api.utils import valida_dia_util, valida_dia_feriado, converter_str_para_datetime


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
    gestao = models.ForeignKey(Gestao, on_delete=models.DO_NOTHING)
    alimentos = models.ManyToManyField(Alimento)
    escolas = models.ManyToManyField(Escola)

    def __str__(self):
        return '{} - {}'.format(self.data, self.descricao)

    class Meta:
        verbose_name = 'Cardápio'
        verbose_name_plural = 'Cardápios'


class StatusSolicitacoes(Enum):
    ESCOLA_SALVOU = 'ESCOLA_SALVOU'
    DRE_A_VALIDAR = 'DRE_A_VALIDAR'
    DRE_APROVADO = 'DRE_APROVADO'
    DRE_REPROVADO = 'DRE_REPROVADO'
    CODAE_A_VALIDAR = 'CODAE_A_VALIDAR'
    CODAE_APROVADO = 'CODAE_APROVADO'
    CODAE_REPROVADO = 'CODAE_REPROVADO'
    TERCEIRIZADA_A_VISUALIZAR = 'TERCEIRIZADA_A_VISUALIZAR'
    TERCEIRIZADA_A_VISUALIZADO = 'TERCEIRIZADA_A_VISUALIZADO'


status_validacao = [StatusSolicitacoes.DRE_A_VALIDAR, StatusSolicitacoes.DRE_APROVADO,
                    StatusSolicitacoes.CODAE_A_VALIDAR,
                    StatusSolicitacoes.CODAE_APROVADO, StatusSolicitacoes.TERCEIRIZADA_A_VISUALIZAR,
                    StatusSolicitacoes.TERCEIRIZADA_A_VISUALIZADO]


class InverterDiaCardapio(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    registro = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.DO_NOTHING, help_text='Usuário que solicitou a altereação')
    escola = models.ForeignKey(Escola, on_delete=models.DO_NOTHING)
    data_de = models.DateField(verbose_name='Data De', help_text='Data do dia inicial da inversão')
    data_para = models.DateField(verbose_name='Data Para', help_text='Data do dia final da inversão')
    descricao = models.TextField('Descrição')
    status = models.CharField(verbose_name='Status',
                              max_length=60,
                              choices=[(status, status.value) for status in StatusSolicitacoes],
                              default=StatusSolicitacoes.DRE_A_VALIDAR)

    @classmethod
    def ja_existe(cls, request):
        de = request.get('data_de')
        para = request.get('data_para')
        escola = request.get('escola')
        return InverterDiaCardapio.objects.filter(data_de=de, data_para=para, escola=escola,
                                                  status__in=status_validacao).exists()

    @classmethod
    def valida_fim_semana(cls, request):
        if valida_dia_util(request.get('data_de')) and valida_dia_util(request.get('data_para')):
            return True
        return False

    @classmethod
    def valida_feriado(cls, request):
        if valida_dia_feriado(request.get('data_de')) and valida_dia_feriado(request.get('data_para')):
            return True
        return False

    @classmethod
    def valida_usuario_escola(cls, usuario: User):
        return Escola.objects.filter(users=usuario).exists()

    @classmethod
    def valida_dia_atual(cls, request):
        if request.get('data_de') == now().date() or request.get('data_para') == now().date():
            return False
        return True

    @classmethod
    def salvar_solicitacao(cls, request, usuario):
        escola = Escola.objects.filter(pk=request.get('escola'))
        if request.get('id'):
            obj = cls.objects.get(pk=request.get('id'))
            obj.usuario = usuario
            obj.data_de = converter_str_para_datetime(request.get('data_de'))
            obj.data_para = converter_str_para_datetime(request.get('data_para'))
            obj.status = StatusSolicitacoes.ESCOLA_SALVOU
            obj.descricao = request.get('descricao'),
            obj.escola = escola.get()
            obj.save()
            return obj
        else:
            obj = InverterDiaCardapio(
                usuario=usuario,
                data_de=converter_str_para_datetime(request.get('data_de')),
                data_para=converter_str_para_datetime(request.get('data_para')),
                status=StatusSolicitacoes.ESCOLA_SALVOU,
                descricao=request.get('descricao'),
                escola=escola.get()
            ).save()
            return obj

    def __str__(self):
        return str(self.uuid)
