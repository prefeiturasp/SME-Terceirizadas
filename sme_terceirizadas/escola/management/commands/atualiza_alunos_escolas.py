import logging
import timeit

import environ
import requests
from django.core.management.base import BaseCommand
from requests import ConnectionError

from ....dados_comuns.constants import DJANGO_EOL_SGP_API_TOKEN, DJANGO_EOL_SGP_API_URL
from ...models import Aluno, Escola, LogRotinaDiariaAlunos

env = environ.Env()

logger = logging.getLogger('sigpae.cmd_atualiza_alunos_escolas')


class Command(BaseCommand):
    help = 'Atualiza os dados de alunos das Escolas baseados na api do SGP'
    headers = {'x-api-eol-key': f'{DJANGO_EOL_SGP_API_TOKEN}'}
    timeout = 10
    contador_alunos = 0
    total_alunos = 0

    def handle(self, *args, **options):
        tic = timeit.default_timer()

        quantidade_alunos_antes = Aluno.objects.all().count()

        self._atualiza_todas_as_escolas()

        quantidade_alunos_atual = Aluno.objects.all().count()

        LogRotinaDiariaAlunos.objects.create(
            quantidade_alunos_antes=quantidade_alunos_antes,
            quantidade_alunos_atual=quantidade_alunos_atual,
        )

        toc = timeit.default_timer()
        result = round(toc - tic, 2)
        if result > 60:
            logger.debug(f'Total time: {round(result // 60, 2)} min')
        else:
            logger.debug(f'Total time: {round(result, 2)} s')

    def _obtem_alunos_escola(self, cod_eol_escola):  # noqa C901
        from datetime import date

        ano = date.today().year
        try:
            r = requests.get(
                f'{DJANGO_EOL_SGP_API_URL}/alunos/ues/{cod_eol_escola}/anosLetivos/{ano}',
                headers=self.headers,
            )
            if r.status_code != 404:
                json = r.json()
                return json
        except ConnectionError as e:
            msg = f'Erro de conexão na api do EOL: {e}'
            logger.error(msg)
            self.stdout.write(self.style.ERROR(msg))

    def _atualiza_alunos_da_escola(self, escola, dados_alunos_escola):
        novos_alunos = {}

        self.total_alunos += len(dados_alunos_escola)
        for registro in dados_alunos_escola:
            self.contador_alunos += 1
            self.stdout.write(
                self.style.SUCCESS(
                    f'{self.contador_alunos} DE UM TOTAL DE {self.total_alunos} ALUNOS'
                )
            )
            aluno = Aluno.objects.filter(codigo_eol=registro['codigoAluno']).first()
            data_nascimento = registro['dataNascimento'].split('T')[0]

            if aluno:
                aluno.nome = registro['nomeAluno'].strip()
                aluno.codigo_eol = registro['codigoAluno']
                aluno.data_nascimento = data_nascimento
                aluno.escola = escola
                aluno.save()
            else:
                obj_aluno = Aluno(
                    nome=registro['nomeAluno'].strip(),
                    codigo_eol=registro['codigoAluno'],
                    data_nascimento=data_nascimento,
                    escola=escola,
                )
                novos_alunos[registro['codigoAluno']] = obj_aluno
        Aluno.objects.bulk_create(novos_alunos.values())

    def _atualiza_todas_as_escolas(self):
        escolas = Escola.objects.filter(diretoria_regional__iniciais='DRE - FB').all()

        total = escolas.count()
        for i, escola in enumerate(escolas):
            logger.debug(f'{i+1}/{total} - {escola}')
            dados_alunos_escola = self._obtem_alunos_escola(escola.codigo_eol)
            if dados_alunos_escola:
                self._atualiza_alunos_da_escola(escola, dados_alunos_escola)
