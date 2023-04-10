import environ
import redis
from django.core.management.base import BaseCommand

from ...models import Escola

env = environ.Env()

REDIS_HOST = env('REDIS_HOST')
REDIS_PORT = env('REDIS_PORT')

redis_connection = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0, charset='utf-8', decode_responses=True)


class Command(BaseCommand):
    help = 'Atualiza cache do Redis com alunos matriculados por escola, faixa etária e período escolar'

    def handle(self, *args, **options):
        iniciais = ['CEI DIRET', 'CEU CEI', 'CEI', 'CCI', 'CCI/CIPS', 'CEI CEU', 'CEU CEMEI', 'CEMEI']
        escolas = Escola.objects.filter(tipo_unidade__iniciais__in=iniciais)
        for escola in escolas:
            self._criar_cache_matriculados_por_faixa(escola)

    def _criar_cache_matriculados_por_faixa(self, escola):
        try:
            msg = f'Atualizando cache para escola {escola.codigo_eol} - {escola.nome}'
            self.stdout.write(self.style.SUCCESS(msg))
            periodos_faixas = escola.alunos_por_periodo_e_faixa_etaria()
            for periodo, qtdFaixas in periodos_faixas.items():
                nome_periodo = self._formatar_periodo_eol(periodo)
                redis_connection.hmset(f'{str(escola.uuid)}:{nome_periodo}', dict(qtdFaixas))
        except Exception as e:
            self.stdout.write(self.style.ERROR(str(e)))

    def _formatar_periodo_eol(self, periodo):
        if periodo == 'MANHÃ':
            return 'MANHA'
        if periodo == 'INTERMEDIÁRIO':
            return 'INTERMEDIARIO'
        return periodo
