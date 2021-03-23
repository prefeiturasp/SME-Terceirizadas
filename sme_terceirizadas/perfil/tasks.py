import logging

from celery import shared_task

from ..eol_servico.utils import EOLException, EOLService
from .models import Cargo, Usuario

logger = logging.getLogger('sigpae.taskPerfil')


def get_usuario(registro_funcional):
    usuario = Usuario.objects.filter(registro_funcional=registro_funcional).first()
    if usuario:
        return usuario


def compara_e_atualiza_dados_do_eol(dados, usuario):
    for dado in dados:
        nome_cargo = dado.get('cargo')
        if usuario.cargo != nome_cargo:
            usuario.desativa_cargo()
            cargo = Cargo.objects.create(usuario=usuario, nome=nome_cargo)
            cargo.ativar_cargo()
            usuario.atualizar_cargo()


@shared_task
def busca_cargo_de_usuario(registro_funcional):
    try:
        usuario = get_usuario(registro_funcional)
        dados = EOLService.get_informacoes_usuario(registro_funcional)
        compara_e_atualiza_dados_do_eol(dados, usuario)

    except EOLException:
        logger.debug(f'Usuario com rf {registro_funcional} não esta cadastro no EOL')
