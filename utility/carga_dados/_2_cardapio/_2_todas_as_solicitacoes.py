"""
    Antes de rodar isso vc deve ter rodado as escolas e as fixtures
"""
import datetime
import random

from faker import Faker

from sme_pratoaberto_terceirizadas.escola.models import Escola, DiretoriaRegional
from sme_pratoaberto_terceirizadas.inclusao_alimentacao.models import InclusaoAlimentacaoContinua, \
    MotivoInclusaoContinua
from sme_pratoaberto_terceirizadas.perfil.models import Usuario

f = Faker('pt-br')
f.seed(420)
hoje = datetime.datetime.today()


def vincula_dre_escola_usuario():
    dres = DiretoriaRegional.objects.filter(id__lte=5)
    escolas = Escola.objects.filter(id__lte=5)
    for dre in dres:
        dre.escolas.set(escolas)
    usuario = Usuario.objects.first()
    usuario.diretorias_regionais.set(dres)
    usuario.escolas.set(escolas)


def _get_random_motivo_continuo():
    return MotivoInclusaoContinua.objects.order_by("?").first()


def _get_random_escola():
    return Escola.objects.filter(id__lte=5).order_by("?").first()


def _get_random_dre():
    return DiretoriaRegional.objects.filter(id__lte=5).order_by("?").first()


def fluxo_escola_felix(obj, user):
    obj.inicia_fluxo(user=user, notificar=True)
    # obj.save()
    obj.dre_aprovou(user=user, notificar=True)
    # obj.save()
    obj.codae_aprovou(user=user, notificar=True)
    # obj.save()
    obj.terceirizada_tomou_ciencia(user=user, notificar=True)
    # obj.save()


def cria_inclusoes_continuas(qtd=50):
    user = Usuario.objects.first()
    for i in range(qtd):
        inclusao_continua = InclusaoAlimentacaoContinua.objects.create(
            motivo=_get_random_motivo_continuo(),
            escola=_get_random_escola(),
            outro_motivo=f.text()[:20],
            descricao=f.text()[:160], criado_por=user,
            dias_semana=[1, 4, 5],
            data_inicial=hoje + datetime.timedelta(
                days=random.randint(1, 15)),
            data_final=hoje + datetime.timedelta(
                days=random.randint(100, 200)))
        fluxo_escola_felix(inclusao_continua, user)


print('-> vinculando escola dre e usuarios')
vincula_dre_escola_usuario()
print('-> criando inclusoes continuas')
cria_inclusoes_continuas()
