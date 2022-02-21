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
            if r.status_code == 200:
                json = r.json()
                return json
            else:
                return []
        except ConnectionError as e:
            msg = f'Erro de conexão na api do EOL: {e}'
            logger.error(msg)
            self.stdout.write(self.style.ERROR(msg))

    def _obtem_matricula_ativa_do_aluno(self, cod_eol_aluno):
        from datetime import date

        ano = date.today().year
        filtros = f'turmas/anosLetivos/{ano}/historico/false/filtrar-situacao/false'
        try:
            r = requests.get(
                f'{DJANGO_EOL_SGP_API_URL}/alunos/{cod_eol_aluno}/{filtros}',
                headers=self.headers,
            )
            if r.status_code == 200:
                json = r.json()
                return json
            else:
                return []
        except ConnectionError as e:
            msg = f'Erro de conexão na api do EOL: {e}'
            logger.error(msg)
            self.stdout.write(self.style.ERROR(msg))

    def _monta_obj_aluno(self, registro, escola, data_nascimento):
        obj_aluno = Aluno(
            nome=registro['nomeAluno'].strip(),
            codigo_eol=registro['codigoAluno'],
            data_nascimento=data_nascimento,
            escola=escola,
        )
        return obj_aluno

    def _atualiza_aluno(self, aluno, registro, data_nascimento, escola):
        aluno.nome = registro['nomeAluno'].strip()
        aluno.codigo_eol = registro['codigoAluno']
        aluno.data_nascimento = data_nascimento
        aluno.escola = escola
        aluno.nao_matriculado = False
        aluno.save()

    def _verifica_se_aluno_esta_matriculado(self, aluno, status_matricula_ativa):
        lista_de_matriculas = self._obtem_matricula_ativa_do_aluno(aluno.codigo_eol)
        if lista_de_matriculas and type(lista_de_matriculas) == list and len(lista_de_matriculas) > 0:
            self._filtra_matricula_ativa(aluno, lista_de_matriculas, status_matricula_ativa)

    def _filtra_matricula_ativa(self, aluno, lista_de_matriculas, status_matricula_ativa):
        for matricula in lista_de_matriculas:
            aluno.nao_matriculado = True
            if matricula['codigoSituacaoMatricula'] in status_matricula_ativa:
                aluno.nome = matricula['nomeAluno'].strip()
                aluno.codigo_eol = matricula['codigoAluno']
                aluno.data_nascimento = matricula['dataNascimento'].split('T')[0]
                aluno.escola = Escola.objects.filter(codigo_eol=matricula['codigoEscola']).first()
                aluno.nao_matriculado = False
                break
        if(aluno.nao_matriculado):
            aluno.escola = None
        aluno.save()

    def _desvincula_matricula_inativa(self, aluno):
        aluno.nao_matriculado = True
        aluno.escola = None
        aluno.save()

    def _atualiza_escola_atribuida(self, registro, aluno, escola, data, status_ativos, status_transferidos):
        if registro['codigoSituacaoMatricula'] in status_ativos:
            self._atualiza_aluno(aluno, registro, data, escola)
        elif registro['codigoSituacaoMatricula'] in status_transferidos:
            self._verifica_se_aluno_esta_matriculado(aluno, status_ativos)
        else:
            self._desvincula_matricula_inativa(aluno)

    def _atualiza_alunos_da_escola(self, escola, dados_alunos_escola):
        novos_alunos = {}
        status_matricula_ativa = [1, 6, 10, 13, 5]
        status_matricula_transferida = [3, 14, 15]

        self.total_alunos += len(dados_alunos_escola)
        for registro in dados_alunos_escola:
            self.contador_alunos += 1
            self.stdout.write(
                self.style.SUCCESS(
                    f'{self.contador_alunos} DE UM TOTAL DE {self.total_alunos} MATRICULAS'
                )
            )
            aluno = Aluno.objects.filter(codigo_eol=registro['codigoAluno']).first()
            data_nascimento = registro['dataNascimento'].split('T')[0]

            if aluno:
                self._atualiza_escola_atribuida(
                    registro, aluno, escola,
                    data_nascimento, status_matricula_ativa,
                    status_matricula_transferida
                )
            else:
                novos_alunos[registro['codigoAluno']] = self._monta_obj_aluno(registro, escola, data_nascimento)

        Aluno.objects.bulk_create(novos_alunos.values())

    def _atualiza_todas_as_escolas(self):
        escolas = Escola.objects.all()

        total = escolas.count()
        for i, escola in enumerate(escolas):
            logger.debug(f'{i+1}/{total} - {escola}')
            dados_alunos_escola = self._obtem_alunos_escola(escola.codigo_eol)
            if dados_alunos_escola and type(dados_alunos_escola) == list and len(dados_alunos_escola) > 0:
                self._atualiza_alunos_da_escola(escola, dados_alunos_escola)
