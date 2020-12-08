import logging
import timeit

import environ
import requests
from django.conf import settings
from django.core.management.base import BaseCommand
from requests import ConnectionError
from utility.carga_dados.helper import progressbar

from ....dados_comuns.constants import DJANGO_EOL_API_TOKEN, DJANGO_EOL_API_URL
from ...models import Aluno, Escola, PeriodoEscolar

env = environ.Env()

logger = logging.getLogger('sigpae.cmd_atualiza_alunos_escolas')


class Command(BaseCommand):
    help = 'Atualiza os dados de alunos das Escolas baseados na api do EOL'
    headers = {'Authorization': f'Token {DJANGO_EOL_API_TOKEN}'}

    PERIODOS = {
        'Integral': 'INTEGRAL',
        'Intermediário': 'INTERMEDIARIO',
        'Manhã': 'MANHA',
        'Noite': 'NOITE',
        'Tarde': 'TARDE',
        'Parcial': 'PARCIAL',
        'Vespertino': 'VESPERTINO',
    }

    def add_arguments(self, parser):
        parser.add_argument(
            '--escola', '-e',
            default=None,
            help='Informar código EOL da escola.'
        )
        parser.add_argument(
            '--progressbar', '-p',
            action='store_true',
            help='Mostra barra de progresso.'
        )

    def handle(self, *args, **options):
        tic = timeit.default_timer()
        if options['escola']:
            self._atualiza_todas_as_escolas(options['escola'], options['progressbar'])
        else:
            self._atualiza_todas_as_escolas(options['progressbar'])

        toc = timeit.default_timer()
        result = round(toc - tic, 2)
        if result > 60:
            logger.debug(f'Total time: {round(result // 60, 2)} min')
        else:
            logger.debug(f'Total time: {round(result, 2)} s')

    def _obtem_alunos_escola(self, cod_eol_escola):  # noqa C901
        try:
            r = requests.get(
                f'{DJANGO_EOL_API_URL}/escola_turma_aluno/{cod_eol_escola}',
                headers=self.headers
            )
            json = r.json()
            if json == 'não encontrado':
                logger.debug('Não encontrado.')
                return
            if not settings.DEBUG:
                logger.debug(f'payload da resposta: {json}')
            return json
        except ConnectionError as e:
            msg = f'Erro de conexão na api do EOL: {e}'
            logger.error(msg)
            self.stdout.write(self.style.ERROR(msg))

    def _atualiza_alunos_da_escola(self, escola, dados_escola, progress_bar=None):
        novos_alunos = []
        # Remove dicionários duplicados da lista.
        # Aconteceu na escola codigo_eol 012874.
        registros = [dict(t) for t in {tuple(d.items()) for d in dados_escola['results']}]

        if progress_bar:
            registros = progressbar(registros, 'Alunos')

        for registro in registros:
            aluno = Aluno.objects.filter(codigo_eol=registro['cd_aluno']).first()
            data_nascimento = registro['dt_nascimento_aluno'].split('T')[0]
            periodo = self.PERIODOS[registro['dc_tipo_turno'].strip()]
            periodo_escolar = PeriodoEscolar.objects.get(nome=periodo)

            if aluno:
                aluno.nome = registro['nm_aluno']
                aluno.codigo_eol = registro['cd_aluno']
                aluno.data_nascimento = data_nascimento
                aluno.escola = escola
                aluno.periodo_escolar = periodo_escolar
                aluno.save()
            else:
                obj_aluno = Aluno(
                    nome=registro['nm_aluno'],
                    codigo_eol=registro['cd_aluno'],
                    data_nascimento=data_nascimento,
                    escola=escola,
                    periodo_escolar=periodo_escolar
                )
                novos_alunos.append(obj_aluno)
        Aluno.objects.bulk_create(novos_alunos)

    def _atualiza_todas_as_escolas(self, codigo_eol_escola=None, progressbar=None):
        if codigo_eol_escola:
            escolas = Escola.objects.filter(codigo_eol=codigo_eol_escola)
        else:
            escolas = Escola.objects.all()

        total = escolas.count()
        for i, escola in enumerate(escolas):
            logger.debug(f'{i+1}/{total} - {escola}')
            dados_escola = self._obtem_alunos_escola(escola.codigo_eol)
            if dados_escola:
                self._atualiza_alunos_da_escola(escola, dados_escola, progressbar)
