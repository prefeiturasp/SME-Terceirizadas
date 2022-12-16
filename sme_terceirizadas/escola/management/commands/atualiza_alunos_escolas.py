import datetime
import logging
import timeit

import environ
import requests
from django.core.management.base import BaseCommand
from requests import ConnectionError

from ....dados_comuns.constants import DJANGO_EOL_SGP_API_TOKEN, DJANGO_EOL_SGP_API_URL
from ...models import Aluno, Escola, LogRotinaDiariaAlunos, PeriodoEscolar

env = environ.Env()

logger = logging.getLogger('sigpae.cmd_atualiza_alunos_escolas')


class Command(BaseCommand):
    help = 'Atualiza os dados de alunos das Escolas baseados na api do SGP'
    headers = {'x-api-eol-key': f'{DJANGO_EOL_SGP_API_TOKEN}'}
    timeout = 10
    contador_alunos = 0
    total_alunos = 0
    status_matricula_ativa = [1, 6, 10, 13]  # status para matrículas ativas
    codigo_turma_regular = 1  # código da turma para matrículas do tipo REGULAR

    def __init__(self):
        """Atualiza os dados de alunos das Escolas baseados na api do SGP."""
        super().__init__()
        lista_tipo_turnos = list(PeriodoEscolar.objects.filter(
            tipo_turno__isnull=False).values_list('tipo_turno', flat=True))
        dict_periodos_escolares_por_tipo_turno = {}
        for tipo_turno in lista_tipo_turnos:
            dict_periodos_escolares_por_tipo_turno[tipo_turno] = PeriodoEscolar.objects.get(tipo_turno=tipo_turno)
        self.dict_periodos_escolares_por_tipo_turno = dict_periodos_escolares_por_tipo_turno

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

    def _obtem_alunos_escola(self, cod_eol_escola, ano_param=None):  # noqa C901
        from datetime import date
        ano = date.today().year
        try:
            r = requests.get(
                f'{DJANGO_EOL_SGP_API_URL}/alunos/ues/{cod_eol_escola}/anosLetivos/{ano_param or ano}',
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
            serie=registro['turmaNome'],
            periodo_escolar=self.dict_periodos_escolares_por_tipo_turno[registro['tipoTurno']]
        )
        return obj_aluno

    def _atualiza_aluno(self, aluno, registro, data_nascimento, escola):
        aluno.nome = registro['nomeAluno'].strip()
        aluno.codigo_eol = registro['codigoAluno']
        aluno.data_nascimento = data_nascimento
        aluno.escola = escola
        aluno.nao_matriculado = False
        aluno.serie = registro['turmaNome']
        aluno.periodo_escolar = self.dict_periodos_escolares_por_tipo_turno[registro['tipoTurno']]
        aluno.save()

    def _desvincular_matriculas(self, alunos):
        for aluno in alunos:
            aluno.nao_matriculado = True
            aluno.escola = None
            aluno.save()

    def aluno_matriculado_prox_ano(self, dados, aluno_nome):
        aluno_encontrado = next((aluno for aluno in dados if aluno['nomeAluno'] == aluno_nome), None)
        return aluno_encontrado and aluno_encontrado['codigoSituacaoMatricula'] in self.status_matricula_ativa

    def _atualiza_alunos_da_escola(self, escola, dados_alunos_escola, dados_alunos_escola_prox_ano):
        novos_alunos = {}
        self.total_alunos += len(dados_alunos_escola)
        codigos_consultados = []
        for registro in dados_alunos_escola:
            self.contador_alunos += 1
            self.stdout.write(
                self.style.SUCCESS(
                    f'{self.contador_alunos} DE UM TOTAL DE {self.total_alunos} MATRICULAS'
                )
            )
            if ((registro['codigoSituacaoMatricula'] in self.status_matricula_ativa or
                self.aluno_matriculado_prox_ano(dados_alunos_escola_prox_ano, registro['nomeAluno'])) and
                    registro['codigoTipoTurma'] == self.codigo_turma_regular):

                codigos_consultados.append(registro['codigoAluno'])
                aluno = Aluno.objects.filter(codigo_eol=registro['codigoAluno']).first()
                data_nascimento = registro['dataNascimento'].split('T')[0]
                if aluno:
                    self._atualiza_aluno(aluno, registro, data_nascimento, escola)
                else:
                    novos_alunos[registro['codigoAluno']] = self._monta_obj_aluno(registro, escola, data_nascimento)

        alunos_nao_consultados = Aluno.objects.filter(escola=escola).exclude(codigo_eol__in=codigos_consultados)
        self._desvincular_matriculas(alunos_nao_consultados)
        Aluno.objects.bulk_create(novos_alunos.values())

    def _atualiza_todas_as_escolas(self):
        escolas = Escola.objects.all()
        proximo_ano = datetime.date.today().year + 1

        total = escolas.count()
        for i, escola in enumerate(escolas):
            logger.debug(f'{i+1}/{total} - {escola}')
            dados_alunos_escola = self._obtem_alunos_escola(escola.codigo_eol)
            dados_alunos_escola_prox_ano = self._obtem_alunos_escola(escola.codigo_eol, proximo_ano)
            if dados_alunos_escola and type(dados_alunos_escola) == list and len(dados_alunos_escola) > 0:
                self._atualiza_alunos_da_escola(escola, dados_alunos_escola, dados_alunos_escola_prox_ano)
