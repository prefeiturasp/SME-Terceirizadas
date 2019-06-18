from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import ugettext_lazy as _

from sme_pratoaberto_terceirizadas.abstract_shareable import Descritivel, RegistroHora


class DiasUteis(object):
    def __init__(self, **kwargs):
        for campo in ('data_cinco_dias_uteis', 'data_dois_dias_uteis'):
            setattr(self, campo, kwargs.get(campo, None))


class DadoLogEvenvos(RegistroHora, Descritivel):
    """Eventos de dados importantes para acompanhamento.
    Ex.: Fulano X a tarefa do tipo Z no dia tal, passando os dados W
    #TODO: categorizar os tipos de evento (Enum)"""
    user = models.ForeignKey(get_user_model(),
                             on_delete=models.DO_NOTHING,
                             null=True)


class Contato(Descritivel):
    """Contatos de um usuário"""
    telefone = models.CharField(_('Telefone'), max_length=11, null=True)
    telefone_celular = models.CharField(_('Telefone Celular'), max_length=11, null=True)
    email = models.EmailField(_('Endereco de Email'), blank=True)


class LocalizacaoCidade(models.Model):
    cidade = models.CharField(_("Cidade"), max_length=80, default='São Paulo')
    estado = models.CharField(_("UF"), max_length=2, default='SP')


class Endereco(models.Model):
    """TODO: usar futuramente https://viacep.com.br/ para preencher automaticamente endereço"""
    nome_rua = models.CharField(_("Nome da Rua"), max_length=256)
    complemento = models.CharField(_("Complemento"), max_length=30)
    distrito = models.CharField(_("Distrito"), max_length=60)
    numero = models.CharField(_("Numero"), max_length=60)
    codigo_postal = models.CharField(_("Postal code"), max_length=9)
    lat = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    lon = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    # for now cant edit city because there is only one: SP
    localizacao_cidade = models.ForeignKey(LocalizacaoCidade,
                                      on_delete=models.DO_NOTHING,
                                      null=True,
                                      editable=False)
