import logging
import time

import environ
from django.core.management import BaseCommand

from sme_terceirizadas.eol_servico.utils import EOLServicoSGP
from sme_terceirizadas.perfil.models import Usuario

logger = logging.getLogger('sigpae.cmd_cria_usuarios_no_coresso')

env = environ.Env()


class Command(BaseCommand):
    help = 'Cria ou atribui acesso ao SIGPAE a usuários servidores (que possuem RF) no CoreSSO'

    def handle(self, *args, **options):
        if env('DJANGO_ENV') != 'production':
            self.stdout.write(self.style.ERROR(f'SOMENTE USUÁRIOS DE PRODUÇÃO PODEM SER CRIADOS EM MASSA NO CORESSO!'))
            return
        self.cria_usuarios_servidores_no_coresso()

    def checa_se_atribui_perfil(self, usuario, atribuidos_qtd):
        if usuario.vinculo_atual.perfil:
            perfil = usuario.vinculo_atual.perfil.nome
            EOLServicoSGP.atribuir_perfil_coresso(login=usuario.username, perfil=perfil)
            atribuidos_qtd += 1

    def cria_usuarios_servidores_no_coresso(self):
        logger.info(f'Inicia criação/atribuição de usuários servidores no CoreSSO.')

        usuarios = Usuario.objects.exclude(
            is_active=False
        ).exclude(
            email__contains='@admin.com'
        ).exclude(
            email__contains='@amcom.com.br'
        ).exclude(
            registro_funcional=None
        ).exclude(
            registro_funcional=''
        )

        logger.info(f'Foram encontrados {usuarios.count()} usuários para serem criados/atribuidos no CoreSSO.')

        usuarios_qtd = 0
        atribuidos_qtd = 0
        for usuario in usuarios:
            try:
                if len(usuario.registro_funcional) == 7:
                    existe_core_sso = EOLServicoSGP.usuario_existe_core_sso(login=usuario.username)
                    if not existe_core_sso:
                        EOLServicoSGP.cria_usuario_core_sso(
                            login=usuario.username,
                            nome=usuario.nome,
                            email=usuario.email,
                            e_servidor=True
                        )
                        logger.info(f'Usuario {usuario.username} criado no CoreSSO.')
                        usuarios_qtd += 1
                    self.checa_se_atribui_perfil(usuario, atribuidos_qtd)
                    time.sleep(1)

            except Exception as e:
                msg = f'Erro ao tentar criar/atribuir usuário {usuario.username} no CoreSSO/SIGPAE: {str(e)}'
                logger.error(msg)

            logger.info(
                f'{usuarios_qtd} usuarios foram criados e {atribuidos_qtd} tiveram perfis atribuidos no CoreSSO.')
