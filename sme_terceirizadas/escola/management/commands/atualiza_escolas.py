import environ
import requests
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from requests import ConnectionError

from ....dados_comuns.constants import DJANGO_EOL_API_TOKEN, DJANGO_EOL_API_URL
from ...models import Escola


def calcula_total_alunos_por_escola(quest_json_data: dict) -> dict:
    escola_total = {}
    escolas_quantidades_alunos = quest_json_data['results']

    for escola_data in escolas_quantidades_alunos:
        codigo_escola = escola_data['cd_escola']
        total_corrente = escola_data['total']
        if codigo_escola not in escola_total:
            escola_total[codigo_escola] = total_corrente
        else:
            escola_total[codigo_escola] += total_corrente

    return escola_total


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

        escola_totais = calcula_total_alunos_por_escola(json)

        for codigo_eol, total in escola_totais.items():
            try:
                escola_object = Escola.objects.get(codigo_eol=codigo_eol)
                if escola_object.quantidade_alunos != total:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Atualizando qtd alunos da escola {escola_object.nome} '
                            f'de {escola_object.quantidade_alunos} para {total}')
                    )
                    escola_object.quantidade_alunos = total
                    escola_object.save()
                else:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Nada a ser feito em {escola_object.nome}')
                    )

            except ObjectDoesNotExist:
                self.stdout.write(self.style.ERROR(f'Escola código EOL: {codigo_eol} não existe no banco ainda'))
                continue
            except IntegrityError as e:
                self.stdout.write(self.style.ERROR(f'Dados inconsistentes: {e}'))
                continue
