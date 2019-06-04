import uuid
from datetime import datetime
from enum import Enum
from django.db import models
from django.utils.translation import ugettext_lazy as _

from sme_pratoaberto_terceirizadas.abstract_shareable import Describable, Activable
from sme_pratoaberto_terceirizadas.food.models import Meal
from sme_pratoaberto_terceirizadas.school.models import School, RegionalDirector
from sme_pratoaberto_terceirizadas.utils import send_notification, async_send_mass_html_mail
from sme_pratoaberto_terceirizadas.users.models import User
from sme_pratoaberto_terceirizadas.terceirizada.models import Lote


class StatusSolicitacao(Enum):
    SAVED = 'SALVO'
    SENDED = 'ENVIADA'
    CANCELED = 'CANCELADA'
    DENIED = 'NEGADO'


class MealKit(models.Model):
    """Kit Lanches"""

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(_('Name'), max_length=160)
    description = models.TextField(_('Description'), blank=True, null=True)
    is_active = models.BooleanField(_('Is Active'), default=True)
    meals = models.ManyToManyField(Meal)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Meal Kit")
        verbose_name_plural = _("Meal Kits")


class OrderMealKit(models.Model):
    """ Solicitação de kit lanche """

    TYPES_STATUS = (('SAVED', 'SALVO'), ('SENDED', 'ENVIADO'), ('CANCELED', 'CANCELADO'), ('DENIED', 'NEGADO'))

    location = models.CharField(_('Order Location'), max_length=160, blank=True, null=True)
    students_quantity = models.IntegerField(_('Students Quantity'))
    order_date = models.DateField(_('Order Date'), blank=True, null=True)
    schools = models.ManyToManyField(School)
    meal_kits = models.ManyToManyField(MealKit)
    observation = models.TextField(_('Observation'), blank=True, null=True)
    status = models.CharField(_('Status'), choices=TYPES_STATUS, default=0, max_length=6)
    scheduled_time = models.CharField(_('Scheduled Time'), max_length=60)
    register = models.DateTimeField(_('Registered'), auto_now_add=True)

    def __str__(self):
        return self.location or self.schools.get().name

    class Meta:
        verbose_name = 'Solicitar Kit Lanche'
        verbose_name_plural = 'Solicitar Kits Lanche'

    @classmethod
    def salvar_solicitacao(cls, data, escola):
        try:
            data_passeio = datetime.strptime(data.get('evento_data'), '%d/%m/%Y').date() if data.get(
                'evento_data') else None
            meals = MealKit.objects.filter(uuid__in=data.get('kit_lanche', None))
            if data.get('id', None):
                obj = cls.objects.get(pk=data.get('id'))
                obj.location = data.get('local_passeio', None)
                obj.students_quantity = data.get('nro_alunos')
                obj.order_date = data_passeio
                obj.observation = data.get('obs')
                obj.scheduled_time = data.get('tempo_passeio')
                for m in meals:
                    obj.meal_kits.add(m)
                obj.schools.add(escola)
                obj.save()
                return obj
            else:
                obj = cls(
                    location=data.get('local_passeio', None),
                    students_quantity=data.get('nro_alunos'),
                    order_date=data_passeio,
                    observation=str(data.get('obs')) if data.get('obs') else None,
                    status='SAVED',
                    scheduled_time=data.get('tempo_passeio')
                )
                obj.save()
                for m in meals:
                    obj.meal_kits.add(m)
                obj.schools.add(escola)
                obj.save()
                return obj
        except ValueError:
            return False

    @classmethod
    def ja_existe_salvo(cls, data, escola):
        try:
            data_passeio = datetime.strptime(data.get('evento_data', None), '%d/%m/%Y').date()
            return cls.objects.filter(schools=escola, order_date=data_passeio, status='SAVED').exists()
        except ValueError:
            return False

    @classmethod
    def valida_duplicidade(cls, data, escola):
        tempo = data.get('tempo_passeio', None)
        data_passeio = datetime.strptime(data.get('evento_data'), '%d/%m/%Y')
        if cls.objects.filter(schools=escola, order_date=data_passeio, status='SENDED',
                              scheduled_time=tempo).count():
            return False
        return True

    @classmethod
    def solicitar_kit_lanche(cls, data, escola, usuario):
        try:
            data_passeio = datetime.strptime(data.get('evento_data', None), '%d/%m/%Y').date()
            meals = MealKit.objects.filter(uuid__in=data.get('kit_lanche', None))
            obj = cls(
                location=data.get('local_passeio', None),
                students_quantity=data.get('nro_alunos', None),
                order_date=data_passeio,
                observation=data.get('obs', None),
                status='SENDED',
                scheduled_time=data.get('tempo_passeio', None)
            )
            obj.save()
            obj.schools.add(escola)
            for m in meals:
                obj.meal_kits.add(m)
            obj.save()
            message = 'Solicitação: {} - Data: {}'.format(obj.location, obj.order_date)
            send_notification(usuario, User.objects.filter(email='mmaia.cc@gmail.com'), 'Teste de nofiticação',
                              message)
            return obj
        except ValueError:
            return False

    @classmethod
    def solicita_kit_lanche_em_lote(cls, data, usuario):
        solicitacoes = cls.objects.filter(pk__in=data['ids'])
        if solicitacoes:
            contador_solicitacoes = 0
            for solicitacao in solicitacoes:
                dado_validador = {'tempo_passeio': solicitacao.scheduled_time,
                                  'evento_data': datetime.strftime(solicitacao.order_date, '%d/%m/%Y')}
                if cls.valida_duplicidade(dado_validador, solicitacao.schools.first()):
                    solicitacao.status = 'SENDED'
                    solicitacao.save()
                    cls.notifica_dres(usuario, solicitacao.schools.first(), solicitacao)
                    contador_solicitacoes += 1
            return contador_solicitacoes

    @classmethod
    def notifica_dres(cls, usuario, escola, solicitacao):
        usuarios_dre = RegionalDirector.object.get(school=escola).users.all()
        email_usuarios_dre = RegionalDirector.objects.filter(school=escola).values_list('users__email')
        data_formatada = datetime.strftime(solicitacao.order_date, '%d/%m/%Y')
        mensagem_notificacao = 'Solicitação kit lanche para a escola {} para {} no dia: {}'.format(escola,
                                                                                                   solicitacao.location,
                                                                                                   data_formatada)
        send_notification(
            usuario,
            usuarios_dre,
            'Solicitação de Kit Lanche da escola: {}'.format(escola),
            mensagem_notificacao
        )

        async_send_mass_html_mail('Solicitação de Kit Lanche da escola: {}'.format(escola), mensagem_notificacao, '',
                                  email_usuarios_dre)


class StatusSolicitacaoUnificada(Describable):
    """Status para Solicitação Unificada"""
    TO_APPROVE = "A APROVAR"
    TO_EDIT = "A EDITAR"
    TO_VISUALIZE = "A VISUALIZAR"
    DENIED_BY_CODAE = "NEGADO PELA CODAE"
    VISUALIZED = "VISUALIZADO"

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Status"
        verbose_name_plural = "Status"


class RazaoSolicitacaoUnificada(Describable, Activable):
    """Motivo para Solicitação Unificada"""

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Razão"
        verbose_name_plural = "Razões"


class SolicitacaoUnificadaFormulario(models.Model):
    """Formulario de Solicitação Unificada de Kit Lanche (DRE)"""
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    criado_por = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    criado_em = models.DateTimeField(auto_now_add=True)
    dia = models.DateField()
    razao = models.ForeignKey(RazaoSolicitacaoUnificada, on_delete=models.DO_NOTHING)
    local_passeio = models.CharField("Local", max_length=200)
    solicitacoes = models.ManyToManyField(OrderMealKit, blank=True)
    pedido_multiplo = models.BooleanField(default=False)
    max_numero_alunos_por_escola = models.IntegerField(blank=True, null=True)
    tempo_passeio = models.CharField("Tempo de Passeio", max_length=60, blank=True, null=True)
    kits_lanche = models.ManyToManyField(MealKit, blank=True)
    obs = models.TextField("Observação", blank=True, null=True)

    def __str__(self):
        return self.dia.strftime("%d/%m/%Y") + ' - ' + self.local_passeio

    @classmethod
    def salvar_formulario(cls, data, usuario):
        try:
            if data.get('id', None):
                obj = cls.objects.get(pk=data.get('id'))
            else:
                obj = cls()
            obj.criado_por = usuario
            dia = data.get('dia')
            razao = data.get('razao')
            obj.dia = datetime.strptime(dia, '%d/%m/%Y').date()
            obj.razao = RazaoSolicitacaoUnificada.objects.get(name=razao)
            obj.local_passeio = data.get('local_passeio')
            obj.obs = data.get('obs', None)
            obj.pedido_multiplo = data.get('pedido_multiplo', False)
            obj.save()
            if obj.pedido_multiplo:
                obj.max_numero_alunos_por_escola = data.get('max_numero_alunos_por_escola')
                obj.tempo_passeio = data.get('tempo_passeio')
                refeicoes = MealKit.objects.filter(uuid__in=data.get('kit_lanche', None))
                for refeicao in refeicoes:
                    obj.kits_lanche.add(refeicao)
                escolas = data.get('escolas')
                for escola in escolas:
                    if escola.get('checked') is True:
                        solicitacao_multiplo_escola = SolicitacaoUnificadaMultiploEscola()
                        escola_obj = School.objects.get(eol_code=escola.get('id'))
                        solicitacao_multiplo_escola.escola = escola_obj
                        solicitacao_multiplo_escola.numero_alunos = escola.get('numero_alunos')
                        solicitacao_multiplo_escola.solicitacao_unificada = obj
                        solicitacao_multiplo_escola.save()
            else:
                escolas = data.get('escolas')
                for escola in escolas:
                    if escola.get('checked') is True:
                        escola_obj = School.objects.get(eol_code=escola.get('id'))
                        escola.pop('id')
                        solicitacao = OrderMealKit.salvar_solicitacao(escola, escola_obj)
                        obj.solicitacoes.add(solicitacao)
            obj.save()
        except ValueError as e:
            print(e)
            return False


class SolicitacaoUnificadaMultiploEscola(models.Model):
    """Par Escola <> Número de estudantes quando Solicitação Unificada é Múltipla"""
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    escola = models.ForeignKey(School, on_delete=models.DO_NOTHING)
    numero_alunos = models.IntegerField()
    solicitacao_unificada = models.ForeignKey(SolicitacaoUnificadaFormulario, on_delete=models.DO_NOTHING,
                                              related_name='escolas')

    def __str__(self):
        return self.escola.name + ' - ' + str(self.numero_alunos)


class SolicitacaoUnificada(models.Model):
    """Solicitacao Unificada de Kit Lanche"""
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    formulario = models.ForeignKey(SolicitacaoUnificadaFormulario, on_delete=models.DO_NOTHING)
    status = models.ForeignKey(StatusSolicitacaoUnificada, on_delete=models.DO_NOTHING)
    lote = models.ForeignKey(Lote, on_delete=models.DO_NOTHING)
