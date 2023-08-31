from datetime import date, timedelta

import environ
import redis
from django.core.management.base import BaseCommand

from ...models import Escola, FaixaEtaria, LogAlunosMatriculadosFaixaEtariaDia, PeriodoEscolar

env = environ.Env()

REDIS_HOST = env('REDIS_HOST')
REDIS_PORT = env('REDIS_PORT')
REDIS_DB = env('REDIS_DB')
REDIS_PREFIX = env('REDIS_PREFIX')

redis_connection = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB,
                                     charset='utf-8', decode_responses=True)


class Command(BaseCommand):
    help_text = 'Atualiza cache do Redis e tabela LogAlunosMatriculadosFaixaEtariaDia '
    help_text += 'com alunos matriculados por escola, faixa etária e período escolar'
    help = help_text

    def handle(self, *args, **options):
        iniciais = ['CEI DIRET', 'CEU CEI', 'CEI', 'CCI', 'CCI/CIPS', 'CEI CEU', 'CEU CEMEI', 'CEMEI']
        escolas = Escola.objects.filter(tipo_unidade__iniciais__in=iniciais)
        for escola in escolas:
            self._criar_cache_matriculados_por_faixa(escola)
            self._salvar_matriculados_por_faixa_dia(escola)

    def _criar_cache_matriculados_por_faixa(self, escola):
        try:
            msg = f'Atualizando cache para escola {escola.codigo_eol} - {escola.nome}'
            self.stdout.write(self.style.SUCCESS(msg))
            periodos_faixas = escola.alunos_por_periodo_e_faixa_etaria()
            for periodo, qtdFaixas in periodos_faixas.items():
                nome_periodo = self._formatar_periodo_eol(periodo)
                redis_connection.hmset(f'{REDIS_PREFIX}-{str(escola.uuid)}-{nome_periodo}', dict(qtdFaixas))
        except Exception as e:
            self.stdout.write(self.style.ERROR(str(e)))

    def _formatar_periodo_eol(self, periodo):
        if periodo == 'MANHÃ':
            return 'MANHA'
        if periodo == 'INTERMEDIÁRIO':
            return 'INTERMEDIARIO'
        return periodo

    def _duplica_dia_anterior(self, escola):
        ontem = date.today() - timedelta(days=1)
        logs = LogAlunosMatriculadosFaixaEtariaDia.objects.filter(
            escola=escola,
            data=ontem - timedelta(days=1)
        )
        for log in logs:
            LogAlunosMatriculadosFaixaEtariaDia.objects.update_or_create(
                escola=escola,
                periodo_escolar=log.periodo_escolar,
                faixa_etaria=log.faixa_etaria,
                data=ontem,
                defaults={
                    'escola': escola,
                    'periodo_escolar': log.periodo_escolar,
                    'faixa_etaria': log.faixa_etaria,
                    'quantidade': log.quantidade,
                    'data': ontem
                }
            )

    def periodos_integral_sem_alunos_pariciais(self, periodos, periodo_parcial):
        if periodos['INTEGRAL'] and periodo_parcial['PARCIAL']:
            chaves_comuns = set(periodo_parcial['PARCIAL'].keys()).intersection(periodos['INTEGRAL'].keys())
            for chave in chaves_comuns:
                periodos['INTEGRAL'][chave] -= periodo_parcial['PARCIAL'][chave]
        return {**periodo_parcial, **periodos}

    def _salvar_matriculados_por_faixa_dia(self, escola):
        try:
            msg = f'Salvando matriculados por faixa da escola {escola.codigo_eol} - {escola.nome}'
            self.stdout.write(self.style.SUCCESS(msg))
            ontem = date.today() - timedelta(days=1)
            periodos_faixas_gerais = escola.alunos_por_periodo_e_faixa_etaria()
            periodos_faixas_parciais = escola.alunos_periodo_parcial_e_faixa_etaria()
            periodos_faixas = self.periodos_integral_sem_alunos_pariciais(
                periodos_faixas_gerais,
                periodos_faixas_parciais
            )
            for periodo, qtd_faixas in periodos_faixas.items():
                periodo_escolar = PeriodoEscolar.objects.get(nome=self._formatar_periodo_eol(periodo))
                for faixa_etaria, quantidade in qtd_faixas.items():
                    LogAlunosMatriculadosFaixaEtariaDia.objects.update_or_create(
                        escola=escola,
                        periodo_escolar=periodo_escolar,
                        faixa_etaria=FaixaEtaria.objects.get(uuid=faixa_etaria),
                        data=ontem,
                        defaults={
                            'escola': escola,
                            'periodo_escolar': periodo_escolar,
                            'faixa_etaria': FaixaEtaria.objects.get(uuid=faixa_etaria),
                            'quantidade': quantidade,
                            'data': ontem
                        }
                    )

        except Exception as e:
            self.stdout.write(self.style.ERROR(str(e)))
            self._duplica_dia_anterior(escola)
