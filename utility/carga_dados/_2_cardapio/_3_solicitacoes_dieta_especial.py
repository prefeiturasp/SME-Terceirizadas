"""
    Antes de rodar isso vc deve ter rodado as escolas e as fixtures e associar usuarios as instituicoes
"""
from base64 import b64encode
import datetime
import random
import string

from django.db import IntegrityError, transaction
from django.core.files.uploadedfile import SimpleUploadedFile
from faker import Faker

from sme_terceirizadas.escola.models import Aluno, Escola
from .helper import base64_encode

from sme_terceirizadas.dieta_especial.models import (
    AlergiaIntolerancia, Anexo, ClassificacaoDieta,
    SolicitacaoDietaEspecial, TipoDieta
)
from sme_terceirizadas.perfil.models import Usuario

f = Faker('pt-br')
f.seed(420)


def fluxo_escola_felix_dieta_especial(obj, user, index):
    obj.inicia_fluxo(user=user, notificar=True)
    if index % 7 == 0:
        obj.codae_nega(user=user, notificar=True)
        return
    else:
        if index % 3 == 0:
            return
        if index % 5 == 0:
            obj.cancelar_pedido(user=user, justificativa='')
            return
        if index % 2 == 1:
            obj.codae_autoriza(user=user, notificar=True)
            return
        if index % 2 == 0:
            obj.codae_autoriza(user=user, notificar=True)
            obj.terceirizada_toma_ciencia(user=user, notificar=True)
            return


def _get_random_from_queryset(qs):
    return qs[random.randint(0, len(qs) - 1)]


tipos_de_dieta = TipoDieta.objects.all()
def _get_random_tipo_de_dieta():
    return _get_random_from_queryset(tipos_de_dieta)


classificacoes_dieta = ClassificacaoDieta.objects.all()
def _get_random_classificacao_de_dieta():
    return _get_random_from_queryset(classificacoes_dieta)


alergias = AlergiaIntolerancia.objects.all()
def _get_random_alergia():
    return _get_random_from_queryset(alergias)


escola = Escola.objects.all()
def _get_random_escola():
    return _get_random_from_queryset(escola)


@transaction.atomic
def cria_solicitacoes_dieta_especial(qtd=50):
    user = Usuario.objects.get(email="escola@admin.com")
    codigos_eol = random.sample(range(100000, 999999), qtd)
    alunos = []
    for index in range(qtd):
        alunos.append(Aluno(
            nome=f.text()[:25],
            codigo_eol=''.join(random.choice(string.digits) for x in range(6)),
            data_nascimento=datetime.date(2015, 10, 19),
            escola=_get_random_escola()
        ))
    Aluno.objects.bulk_create(alunos)

    with open('sme_terceirizadas/static/files/425-cuidado-area-de-teste.jpg', 'rb') as image_file:
        test_file = SimpleUploadedFile(
            f.file_name(extension="jpg"),
            image_file.read()
        )

    for index in range(qtd):
        if index % 10 == 0:
            print(f'{index / 10}% COMPLETO')

        for i in range(random.randint(1, 7)):
            tipo_dieta_1 = _get_random_tipo_de_dieta()
            tipo_dieta_2 = _get_random_tipo_de_dieta()
            alergia_1 = _get_random_alergia()
            alergia_2 = _get_random_alergia()
            solicitacao_dieta_especial = SolicitacaoDietaEspecial.objects.create(
                criado_por=user,
                nome_completo_pescritor=f.text()[:25],
                registro_funcional_pescritor=''.join(random.choice(string.digits) for x in range(6)),
                registro_funcional_nutricionista=''.join(random.choice(string.digits) for x in range(6)),
                observacoes=f.text()[:25],
                classificacao=_get_random_classificacao_de_dieta(),
                aluno=alunos[index],
                ativo=True if random.randint(0, 1) == 1 else False
            )
            solicitacao_dieta_especial.alergias_intolerancias.add(alergia_1, alergia_2)
            solicitacao_dieta_especial.tipos.add(tipo_dieta_1, tipo_dieta_2)

            for eh_laudo_medico in [True, False]:
                Anexo.objects.create(
                    solicitacao_dieta_especial=solicitacao_dieta_especial,
                    arquivo=test_file,
                    nome=f.file_name(extension="jpg"),
                    eh_laudo_medico=eh_laudo_medico
                )
            fluxo_escola_felix_dieta_especial(solicitacao_dieta_especial, user, index)

QTD_PEDIDOS = 1000

criar_pedidos = input('Criar solicitacoes dieta especial? (S/N)?')
if criar_pedidos.upper() == 'S':
    print('-> criando solicitacoes dieta especial')
    cria_solicitacoes_dieta_especial(QTD_PEDIDOS)
