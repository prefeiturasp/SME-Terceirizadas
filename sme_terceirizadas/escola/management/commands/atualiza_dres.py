import environ
import requests
from django.core.management.base import BaseCommand

from ...models import DiretoriaRegional

env = environ.Env()


class Command(BaseCommand):
    help = 'Atualiza os dados das Diretorias Regionais baseados na api do EOL'

    def handle(self, *args, **options):
        headers = {'Authorization': f'Token {env("DJANGO_EOL_API_TOKEN")}'}

        r = requests.get(f'{env("DJANGO_EOL_API_URL")}/dres/', headers=headers)
        json = r.json()

        for diret in json['results']:
            codigo_dre = diret['cod_dre'].strip()
            sigla_dre = diret['sg_dre'].strip()
            dre_nome = diret['dre'].strip()

            dre_object, created = DiretoriaRegional.objects.get_or_create(codigo_eol=codigo_dre)
            dre_object.iniciais = sigla_dre
            dre_object.nome = dre_nome
            dre_object.save()

            if created:
                self.stdout.write(self.style.SUCCESS(f'Diretoria regional criada.. {dre_object}"' % diret))
            else:
                self.stdout.write(self.style.SUCCESS(f'Diretoria regional atualizada.. {dre_object}"' % diret))
