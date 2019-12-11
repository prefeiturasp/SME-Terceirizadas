import logging

import environ
import requests
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from requests import ConnectionError

from ....dados_comuns.constants import DJANGO_EOL_API_TOKEN, DJANGO_EOL_API_URL
from ...models import DiretoriaRegional, Escola

env = environ.Env()

logger = logging.getLogger('sigpae.cmd_atualiza_dados_escolas')


class Command(BaseCommand):
    help = 'Atualiza os dados das Escolas baseados na api do EOL'

    def handle(self, *args, **options):
        headers = {'Authorization': f'Token {DJANGO_EOL_API_TOKEN}'}

        try:
            r = requests.get(f'{DJANGO_EOL_API_URL}/escolas_terceirizadas/', headers=headers)
            json = r.json()
            logger.debug(f'payload da resposta: {json}')
        except ConnectionError as e:
            msg = f'Erro de conexão na api do  EOL: {e}'
            logger.error(msg)
            self.stdout.write(self.style.ERROR(msg))
            return

        self._atualiza_dre_da_escola(json)
        self._atualiza_dados_da_escola(json)

    def _atualiza_dados_da_escola(self, json):  # noqa C901
        for escola_json in json['results']:
            codigo_eol_escola = escola_json['cd_unidade_educacao'].strip()
            nome_unidade_educacao = escola_json['nm_unidade_educacao'].strip()
            tipo_ue = escola_json['sg_tp_escola'].strip()
            nome_escola = f'{tipo_ue} {nome_unidade_educacao}'
            try:
                escola_object = Escola.objects.get(codigo_eol=codigo_eol_escola)
            except ObjectDoesNotExist:
                msg = f'Escola código EOL: {codigo_eol_escola} não existe no banco ainda'
                self.stdout.write(self.style.ERROR(msg))
                logger.debug(msg)
                continue
            if escola_object.nome != nome_escola:
                msg = f'Atualizando nome da escola {escola_object} para {nome_escola}'
                self.stdout.write(self.style.SUCCESS(msg))
                logger.debug(msg)
                escola_object.nome = nome_escola
                escola_object.save()

    def _atualiza_dre_da_escola(self, json):  # noqa C901
        for escola_json in json['results']:
            codigo_eol_escola = escola_json['cd_unidade_educacao'].strip()
            codigo_eol_dre = escola_json['cod_dre'].strip()
            try:
                escola_object = Escola.objects.get(codigo_eol=codigo_eol_escola)
            except ObjectDoesNotExist:
                msg = f'Escola código EOL: {codigo_eol_escola} não existe no banco ainda'
                logger.debug(msg)
                self.stdout.write(self.style.ERROR(msg))
                continue
            if escola_object.diretoria_regional.codigo_eol != codigo_eol_dre:
                try:
                    diretoria_regional_object = DiretoriaRegional.objects.get(codigo_eol=codigo_eol_dre)
                    msg = f'Escola {escola_object} mudada de DRE {escola_object.diretoria_regional} para {diretoria_regional_object}'  # noqa E501
                    logger.debug(msg)
                    escola_object.diretoria_regional = diretoria_regional_object
                    escola_object.save()
                except ObjectDoesNotExist:
                    msg = f'DiretoriaRegional código EOL: {codigo_eol_dre} não existe no banco ainda'
                    self.stdout.write(self.style.ERROR(msg))
                    continue
