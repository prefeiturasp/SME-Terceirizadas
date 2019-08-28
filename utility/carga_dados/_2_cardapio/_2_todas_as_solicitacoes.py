"""
    Antes de rodar isso vc deve ter rodado as escolas e as fixtures
"""
import datetime
import random

import numpy as np
from faker import Faker

from sme_pratoaberto_terceirizadas.cardapio.models import TipoAlimentacao, InversaoCardapio, Cardapio
from sme_pratoaberto_terceirizadas.escola.models import Escola, DiretoriaRegional, PeriodoEscolar, Codae
from sme_pratoaberto_terceirizadas.inclusao_alimentacao.models import InclusaoAlimentacaoContinua, \
    MotivoInclusaoContinua, GrupoInclusaoAlimentacaoNormal, QuantidadePorPeriodo, InclusaoAlimentacaoNormal, \
    MotivoInclusaoNormal
from sme_pratoaberto_terceirizadas.kit_lanche.models import MotivoSolicitacaoUnificada, SolicitacaoKitLancheUnificada, \
    SolicitacaoKitLanche, KitLanche, SolicitacaoKitLancheAvulsa
from sme_pratoaberto_terceirizadas.perfil.models import Usuario

f = Faker('pt-br')
f.seed(420)
hoje = datetime.datetime.today()


def vincula_dre_escola_usuario():
    dres = DiretoriaRegional.objects.filter(pk=1)
    escolas = Escola.objects.filter(pk=1)
    codae, created = Codae.objects.get_or_create(nome='teste')
    for dre in dres:
        dre.escolas.set(escolas)
    usuario = Usuario.objects.first()
    usuario.diretorias_regionais.set(dres)
    usuario.escolas.set(escolas)

    codae.usuarios.set([usuario])


def _get_random_cardapio():
    return Cardapio.objects.order_by("?").first()


def _get_random_motivo_continuo():
    return MotivoInclusaoContinua.objects.order_by("?").first()


def _get_kit_lanches():
    return KitLanche.objects.all()


def _get_random_motivo_normal():
    return MotivoInclusaoNormal.objects.order_by("?").first()


def _get_random_motivo_unificado_kit_lanche():
    return MotivoSolicitacaoUnificada.objects.order_by("?").first()


def _get_random_escola():
    return Escola.objects.filter(id__lte=5).order_by("?").first()


def _get_random_dre():
    return DiretoriaRegional.objects.filter(id__lte=5).order_by("?").first()


def _get_random_periodo_escolar():
    return PeriodoEscolar.objects.order_by("?").first()


def _get_random_tipos_alimentacao():
    num_alimentacoes = random.randint(2, 5)
    alimentacoes = []
    for i in range(num_alimentacoes):
        alim = TipoAlimentacao.objects.order_by("?").first()
        alimentacoes.append(alim)
    return alimentacoes


def fluxo_escola_felix(obj, user):
    # print(f'aplicando fluxo ESCOLA feliz em {obj}')
    obj.inicia_fluxo(user=user, notificar=True)
    if random.random() >= 0.1:
        obj.dre_aprovou(user=user, notificar=True)
        if random.random() >= 0.2:
            obj.codae_aprovou(user=user, notificar=True)
            if random.random() >= 0.3:
                obj.terceirizada_tomou_ciencia(user=user, notificar=True)


def fluxo_dre_felix(obj, user):
    # print(f'aplicando fluxo DRE feliz em {obj}')
    obj.inicia_fluxo(user=user, notificar=True)
    if random.random() >= 0.1:
        obj.codae_aprovou(user=user, notificar=True)
        if random.random() >= 0.3:
            obj.terceirizada_tomou_ciencia(user=user, notificar=True)


def fluxo_escola_loop(obj, user):
    # print(f'aplicando fluxo loop revisao dre-escola em {obj}')
    obj.inicia_fluxo(user=user, notificar=True)
    obj.dre_pediu_revisao(user=user, notificar=True)
    obj.escola_revisou(user=user, notificar=True)
    obj.dre_aprovou(user=user, notificar=True)


def cria_inclusoes_continuas(qtd=50):
    user = Usuario.objects.first()
    for i in range(qtd):
        inclusao_continua = InclusaoAlimentacaoContinua.objects.create(
            motivo=_get_random_motivo_continuo(),
            escola=_get_random_escola(),
            outro_motivo=f.text()[:20],
            descricao=f.text()[:160], criado_por=user,
            dias_semana=list(np.random.randint(6, size=4)),
            data_inicial=hoje + datetime.timedelta(
                days=random.randint(1, 30)),
            data_final=hoje + datetime.timedelta(
                days=random.randint(100, 200)))

        q = QuantidadePorPeriodo.objects.create(
            periodo_escolar=_get_random_periodo_escolar(),
            numero_alunos=random.randint(10, 200),
            inclusao_alimentacao_continua=inclusao_continua
        )
        q.tipos_alimentacao.set(_get_random_tipos_alimentacao())

        fluxo_escola_felix(inclusao_continua, user)


def cria_inclusoes_normais(qtd=50):
    user = Usuario.objects.first()
    for i in range(qtd):
        grupo_inclusao_normal = GrupoInclusaoAlimentacaoNormal.objects.create(
            descricao=f.text()[:160],
            criado_por=user,
            escola=_get_random_escola()
        )
        q = QuantidadePorPeriodo.objects.create(
            periodo_escolar=_get_random_periodo_escolar(),
            numero_alunos=random.randint(10, 200),
            grupo_inclusao_normal=grupo_inclusao_normal
        )
        q.tipos_alimentacao.set(_get_random_tipos_alimentacao())
        InclusaoAlimentacaoNormal.objects.create(
            motivo=_get_random_motivo_normal(),
            outro_motivo=f.text()[:40],
            grupo_inclusao=grupo_inclusao_normal,
            data=hoje + datetime.timedelta(days=random.randint(1, 30))
        )
        fluxo_escola_felix(grupo_inclusao_normal, user)


def cria_solicitacoes_kit_lanche_unificada(qtd=50):
    user = Usuario.objects.first()
    for i in range(qtd):
        base = SolicitacaoKitLanche.objects.create(
            data=hoje + datetime.timedelta(days=random.randint(1, 30)),
            motivo=f.text()[:40],
            descricao=f.text()[:160],
            tempo_passeio=SolicitacaoKitLanche.QUATRO)
        kits = _get_kit_lanches()[:2]
        base.kits.set(kits)

        unificada = SolicitacaoKitLancheUnificada.objects.create(
            criado_por=user,
            motivo=_get_random_motivo_unificado_kit_lanche(),
            outro_motivo=f.text()[:40],
            quantidade_max_alunos_por_escola=666,
            local=f.text()[:150],
            lista_kit_lanche_igual=True,
            diretoria_regional=_get_random_dre(),
            solicitacao_kit_lanche=base,
        )
        fluxo_dre_felix(unificada, user)


def cria_solicitacoes_kit_lanche_avulsa(qtd=50):
    user = Usuario.objects.first()
    for i in range(qtd):
        base = SolicitacaoKitLanche.objects.create(
            data=hoje + datetime.timedelta(days=random.randint(1, 30)),
            motivo=f.text()[:40],
            descricao=f.text()[:160],
            tempo_passeio=SolicitacaoKitLanche.QUATRO)
        kits = _get_kit_lanches()[:2]
        base.kits.set(kits)
        avulsa = SolicitacaoKitLancheAvulsa.objects.create(
            criado_por=user,
            quantidade_alunos=random.randint(20, 200),
            local=f.text()[:150],
            escola=_get_random_escola(),
            solicitacao_kit_lanche=base)
        fluxo_escola_felix(avulsa, user)


# cardapio_de = models.ForeignKey(Cardapio, on_delete=models.DO_NOTHING,
#                                     blank=True, null=True,
#                                     related_name='cardapio_de')
#     cardapio_para = models.ForeignKey(Cardapio, on_delete=models.DO_NOTHING,
#                                       blank=True, null=True,
#                                       related_name='cardapio_para')
#     escola = models.ForeignKey('escola.Escola', blank=True, null=True,
#                                on_delete=models.DO_NOTHING)

def cria_inversoes_cardapio(qtd=50):
    user = Usuario.objects.first()
    for i in range(qtd):
        inversao = InversaoCardapio(
            criado_por=user,
            observacao=f.text()[:100],
            motivo=f.text()[:40],
            escola=_get_random_escola(),
            cardapio_de=_get_random_cardapio(),
            cardapio_para=_get_random_cardapio())
        fluxo_escola_felix(inversao, user)


# def cria_alteracoes_cardapio(qtd=50):
#     user = Usuario.objects.first()
#     for i in range(qtd):
#         alteracao_cardapio = AlteracaoCardapio(
#             criado_por=user,
#             observacao=f.text()[:100],
#             motivo=f.text()[:40],
#             escola=_get_random_escola(),
#             cardapio_de=_get_random_cardapio(),
#             cardapio_para=_get_random_cardapio())
#         fluxo_escola_felix(alteracao_cardapio, user)


print('-> vinculando escola dre e usuarios')
vincula_dre_escola_usuario()
print('-> criando inclusoes continuas')
cria_inclusoes_continuas(666)
print('-> criando inclusoes normais')
cria_inclusoes_normais(666)
print('-> criando solicicitacoes kit lanche unificada')
cria_solicitacoes_kit_lanche_unificada(666)
print('-> criando solicicitacoes kit lanche avulsa')
cria_solicitacoes_kit_lanche_avulsa(666)
print('-> criando inversoes de cardapio')
cria_inversoes_cardapio(666)
