import uuid
from datetime import datetime
from enum import Enum
from django.db import models
from django.utils.translation import ugettext_lazy as _

from sme_pratoaberto_terceirizadas.abstract_shareable import Describable
from sme_pratoaberto_terceirizadas.food.models import Meal
from sme_pratoaberto_terceirizadas.school.models import School, RegionalDirector
from sme_pratoaberto_terceirizadas.utils import send_notification, async_send_mass_html_mail
from sme_pratoaberto_terceirizadas.users.models import User


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

    location = models.CharField(_('Order Location'), max_length=160)
    students_quantity = models.IntegerField(_('Students Quantity'))
    order_date = models.DateField(_('Order Date'))
    schools = models.ManyToManyField(School)
    meal_kits = models.ManyToManyField(MealKit)
    observation = models.TextField(_('Observation'), blank=True, null=True)
    status = models.CharField(_('Status'), choices=TYPES_STATUS, default=0, max_length=6)
    scheduled_time = models.CharField(_('Scheduled Time'), max_length=60)
    register = models.DateTimeField(_('Registered'), auto_now_add=True)

    def __str__(self):
        return self.location

    class Meta:
        verbose_name = 'Solicitar Kit Lanche'
        verbose_name_plural = 'Solicitar Kits Lanche'

    @classmethod
    def salvar_solicitacao(cls, data, escola):
        try:
            data_passeio = datetime.strptime(data.get('evento_data', None), '%d/%m/%Y').date()
            meals = MealKit.objects.filter(uuid__in=data.get('kit_lanche', None))
            if data.get('id', None):
                obj = cls.objects.get(pk=data.get('id'))
                obj.location = data.get('local_passeio')
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
                    location=data.get('local_passeio'),
                    students_quantity=data.get('nro_alunos'),
                    order_date=data_passeio,
                    observation=str(data.get('obs')),
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
            return cls.objects.filter(schools=escola, order_date=data_passeio, status='SAVED').count()
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
        if 'ids' in data:
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
        return False

    @classmethod
    def notifica_dres(cls, usuario, escola, solicitacao):
        usuarios_dre = RegionalDirector.objects.filter(school=escola).distinct().values_list('users')
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
