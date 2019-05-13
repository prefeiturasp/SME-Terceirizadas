from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import ugettext_lazy as _

from sme_pratoaberto_terceirizadas.abstract_shareable import Describable, TimestampAble


class WorkingDays(object):
    def __init__(self, **kwargs):
        for field in ('date_five_working_days', 'date_two_working_days'):
            setattr(self, field, kwargs.get(field, None))


class LogEventData(TimestampAble, Describable):
    """Eventos de dados importantes para acompanhamento.
    Ex.: Fulano X a tarefa do tipo Z no dia tal, passando os dados W
    #TODO: categorizar os tipos de evento (Enum)"""
    user = models.ForeignKey(get_user_model(),
                             on_delete=models.DO_NOTHING,
                             null=True)


class Contact(Describable):
    """Contatos de um usuário"""
    name = models.CharField(_("Name"), max_length=80)
    phone = models.CharField(_('Phone'), max_length=11, null=True)
    mobile_phone = models.CharField(_('Mobile phone'), max_length=11, null=True)
    email = models.EmailField(_('email address'), blank=True)


class CityLocation(models.Model):
    city = models.CharField(_("City"), max_length=80, default='São Paulo')
    state = models.CharField(_("UF"), max_length=2, default='SP')


class Address(models.Model):
    """TODO: usar futuramente https://viacep.com.br/ para preencher automaticamente endereço"""
    street_name = models.CharField(_("Street name"), max_length=256)
    complement = models.CharField(_("Complement"), max_length=30)
    district = models.CharField(_("District"), max_length=60)
    number = models.CharField(_("Number"), max_length=20)
    postal_code = models.CharField(_("Postal code"), max_length=9)
    lat = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    lon = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    # for now cant edit city because there is only one: SP
    city_location = models.ForeignKey(CityLocation,
                                      on_delete=models.DO_NOTHING,
                                      null=True,
                                      editable=False)


# from django.core.mail.backends.smtp import EmailBackend


class EmailConfiguration(models.Model):
    """Para salvar configurações de email do terceirizadas"""
    host = models.CharField(_("Host"), max_length=100)
    port = models.IntegerField(_("Port"))
    username = models.EmailField(_("Username"), max_length=100)
    password = models.CharField(_("Password"), max_length=100)
    from_email = models.EmailField(_("Email"), max_length=100)

    # default
    use_tls = models.BooleanField(_("Use TLS"), default=False)
    fail_silently = models.BooleanField(_("Fail silently"), default=False)
    use_ssl = models.BooleanField(_("Use SSL"), default=False)
    timeout = models.IntegerField(_("Timeout"), default=30)

    # def send_test_email(self):
    #     backend = EmailBackend(host=self.host, port=self.port, username=self.username,
    #                            password=self.password, use_tls=self.use_tls,
    #                            fail_silently=self.fail_silently)
