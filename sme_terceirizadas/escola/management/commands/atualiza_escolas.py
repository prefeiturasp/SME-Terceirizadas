import environ
import requests
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from requests import ConnectionError

from sme_terceirizadas.escola.management.commands.helper import calcula_total_alunos_por_escola_por_periodo
from sme_terceirizadas.escola.models import EscolaPeriodoEscolar, PeriodoEscolar

from ....dados_comuns.constants import DJANGO_EOL_API_TOKEN, DJANGO_EOL_API_URL
from ...models import Escola

env = environ.Env()


class Command(BaseCommand):
    help = 'Atualiza os dados das Escolas baseados na api do EOL'

    # TODO: simplificar esse metodo, está complexo
    def handle(self, *args, **options):  # noqa C901
        headers = {'Authorization': f'Token {DJANGO_EOL_API_TOKEN}'}

        try:
            r = requests.get(f'{DJANGO_EOL_API_URL}/total_alunos/', headers=headers)
            json = r.json()
        except ConnectionError as e:
            self.stdout.write(self.style.ERROR(f'Erro de conexão na api do  EOL: {e}'))
            return

        escola_totais = calcula_total_alunos_por_escola_por_periodo(json)
        # '000078': {'manha': 163, 'intermediario': 161, 'tarde': 0, 'vespertino': 186, 'noite': 175, 'integral': 0, 'total': 685}

        for codigo_eol, dados in escola_totais.items():
            total_alunos_periodo = dados.pop('total')
            try:
                escola_object = Escola.objects.get(codigo_eol=codigo_eol)
                for periodo_escolar_str, quantidade_alunos_periodo in dados.items():
                    periodo_escolar_object = PeriodoEscolar.objects.get(nome=periodo_escolar_str.upper())
                    escola_periodo, created = EscolaPeriodoEscolar.objects.get_or_create(
                        periodo_escolar=periodo_escolar_object, escola=escola_object
                    )
                    if escola_periodo.quantidade_alunos != quantidade_alunos_periodo:
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'Atualizando qtd alunos da escola {escola_object.nome} '
                                f'de {escola_periodo.quantidade_alunos} para {quantidade_alunos_periodo} no'
                                f'período da {periodo_escolar_object.nome}')
                        )
                        escola_periodo.quantidade_alunos = quantidade_alunos_periodo
                        escola_periodo.save()
                if escola_object.quantidade_alunos != total_alunos_periodo:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Atualizando qtd TOTAL alunos da escola {escola_object.nome} '
                            f'de {escola_object.quantidade_alunos} para {total_alunos_periodo}')
                    )
                    escola_object.quantidade_alunos = total_alunos_periodo
                    escola_object.save()

            except ObjectDoesNotExist:
                self.stdout.write(self.style.ERROR(f'Escola código EOL: {codigo_eol} não existe no banco ainda'))
                continue
            except IntegrityError as e:
                self.stdout.write(self.style.ERROR(f'Dados inconsistentes: {e}'))
                continue
