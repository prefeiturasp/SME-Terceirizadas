from django.core.management.base import BaseCommand
from utility.carga_dados.usuarios import cria_usuarios
from utility.carga_dados.cardapio.importa_dados import cria_motivoalteracaocardapio
from utility.carga_dados.cardapio.importa_dados import cria_motivosuspensao
from utility.carga_dados.cardapio.importa_dados import cria_tipo_alimentacao
from utility.carga_dados.dados_comuns.importa_dados import cria_contatos
from utility.carga_dados.dados_comuns.importa_dados import cria_templatemensagem
from utility.carga_dados.escola.importa_dados import cria_diretorias_regionais
from utility.carga_dados.escola.importa_dados import cria_lotes
from utility.carga_dados.escola.importa_dados import cria_subprefeituras
from utility.carga_dados.escola.importa_dados import cria_tipos_gestao
from utility.carga_dados.inclusao_alimentacao.importa_dados import cria_motivo_inclusao_continua
from utility.carga_dados.inclusao_alimentacao.importa_dados import cria_motivo_inclusao_normal


class Command(BaseCommand):
    help = 'Importa dados iniciais no banco de dados.'

    def handle(self, *args, **options):
        self.stdout.write('Importando dados...')
        cria_usuarios()
        cria_motivoalteracaocardapio()
        cria_motivosuspensao()
        cria_tipo_alimentacao()
        cria_contatos()
        cria_templatemensagem()
        cria_diretorias_regionais()
        cria_lotes()
        cria_subprefeituras()
        cria_tipos_gestao()
        cria_motivo_inclusao_continua()
        cria_motivo_inclusao_normal()
