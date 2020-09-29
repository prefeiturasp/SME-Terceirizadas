from django.conf import settings
from django.core.management.base import BaseCommand
from utility.carga_dados.usuarios import cria_usuarios
from utility.carga_dados.cardapio.importa_dados import cria_motivoalteracaocardapio  # noqa
from utility.carga_dados.cardapio.importa_dados import cria_motivosuspensao
from utility.carga_dados.cardapio.importa_dados import cria_tipo_alimentacao
from utility.carga_dados.dados_comuns.importa_dados import cria_contatos
from utility.carga_dados.dados_comuns.importa_dados import cria_templatemensagem  # noqa
from utility.carga_dados.escola.importa_dados import cria_diretorias_regionais
from utility.carga_dados.escola.importa_dados import cria_lotes
from utility.carga_dados.escola.importa_dados import cria_subprefeituras
from utility.carga_dados.escola.importa_dados import cria_tipos_gestao
from utility.carga_dados.inclusao_alimentacao.importa_dados import cria_motivo_inclusao_continua  # noqa
from utility.carga_dados.inclusao_alimentacao.importa_dados import cria_motivo_inclusao_normal  # noqa
from utility.carga_dados.kit_lanche.importa_dados import cria_kit_lanche_item
from utility.carga_dados.kit_lanche.importa_dados import cria_kit_lanche
from utility.carga_dados.produto.importa_dados import cria_informacao_nutricional  # noqa
from utility.carga_dados.produto.importa_dados import cria_tipo_informacao_nutricional  # noqa
from utility.carga_dados.terceirizada.importa_dados import cria_terceirizadas


class Command(BaseCommand):
    help = 'Importa dados iniciais no banco de dados.'

    def handle(self, *args, **options):
        self.stdout.write('Importando dados...')

        # A ordem dos métodos é importante!
        # Por isso um monte de if.
        if settings.DEBUG:
            cria_usuarios()  # Dev

        cria_motivoalteracaocardapio()
        cria_motivosuspensao()
        cria_tipo_alimentacao()

        if settings.DEBUG:
            cria_contatos()
            cria_templatemensagem()

        cria_diretorias_regionais()
        cria_tipos_gestao()

        cria_terceirizadas()

        cria_lotes()
        cria_subprefeituras()
        cria_motivo_inclusao_continua()
        cria_motivo_inclusao_normal()

        if settings.DEBUG:
            cria_kit_lanche_item()
            cria_kit_lanche()

        cria_tipo_informacao_nutricional()
        cria_informacao_nutricional()

        # if settings.DEBUG:
        #     # terceirizada
        #     cria_contratos()  # Fazer
        #     cria_editais()  # Fazer
        #     cria_nutricionistas()  # Fazer

        # if settings.DEBUG:
        #     # terceirizada
        #     cria_vigencias()  # Fazer

        # Produto
        # cria_diagnosticos()  # Fazer

        # Escola
        # TODO para DEV
