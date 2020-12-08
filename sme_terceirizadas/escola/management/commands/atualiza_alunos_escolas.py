import environ
import logging
import requests
import timeit
from django.core.management.base import BaseCommand
from requests import ConnectionError

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

    def handle(self, *args, **options):
        tic = timeit.default_timer()
        self._atualiza_todas_as_escolas()
        toc = timeit.default_timer()
        result = round(toc - tic, 2)
        if result > 60:
            print('Total time:', round(result // 60, 2))
        else:
            print('Total time:', round(result, 2))

    def _obtem_alunos_escola(self, cod_eol_escola):
        try:
            r = requests.get(
                f'{DJANGO_EOL_API_URL}/escola_turma_aluno/{cod_eol_escola}',
                headers=self.headers
            )
            json = r.json()
            if json == 'não encontrado':
                return
            logger.debug(f'payload da resposta: {json}')
            return json
        except ConnectionError as e:
            msg = f'Erro de conexão na api do EOL: {e}'
            logger.error(msg)
            self.stdout.write(self.style.ERROR(msg))
            return

    def _atualiza_alunos_da_escola(self, escola, dados_escola):
        novos_alunos = []
        # Remove dicionários duplicados da lista.
        # Aconteceu na escola codigo_eol 012874.
        registros = [dict(t) for t in {tuple(d.items()) for d in dados_escola['results']}]

        for i, registro in enumerate(registros):
            print(i, registro['cd_aluno'], registro['nm_aluno'])
            with open('alunos_teste.txt', 'a') as f:
                f.write(f"{str(i)}, {registro['cd_aluno']}, {registro['nm_aluno']}")
                f.write('\n')

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

    def _atualiza_todas_as_escolas(self):
        escolas = Escola.objects.all()
        for i, escola in enumerate(escolas):
            print(i, 'escola:', escola)
            dados_escola = self._obtem_alunos_escola(escola.codigo_eol)
            with open('escolas_teste.txt', 'a') as f:
                f.write(str(i))
                f.write('\n')
                f.write(str(escola.codigo_eol))
                f.write('\n')
            if dados_escola:
                self._atualiza_alunos_da_escola(escola, dados_escola)
