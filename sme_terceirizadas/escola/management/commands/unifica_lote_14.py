import logging

import environ
from django.core.management import BaseCommand

from sme_terceirizadas.escola.models import Lote

logger = logging.getLogger('sigpae.cmd_suja_base')

env = environ.Env()


class Command(BaseCommand):
    help = 'Unifica os lotes 14A e 14B em 14'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS(f'Renomeando lote 14A para 14'))
        lote_14_a = Lote.objects.get(nome__icontains='14 A')
        lote_14_a.nome = 'Lote 14'
        lote_14_a.save()
        lote_14_b = Lote.objects.get(nome__icontains='14 B')

        self.stdout.write(self.style.SUCCESS(f'*** Geral ***'))

        self.stdout.write(self.style.SUCCESS(f'{lote_14_b.escolas.count()} escolas passadas do Lote 14B para o 14'))
        lote_14_b.escolas.update(lote=lote_14_a)
        self.stdout.write(self.style.SUCCESS(f'{lote_14_b.contratos_do_lote.count()} '
                                             f'referências de contratos do lote 14B excluídas'))
        for contrato in lote_14_b.contratos_do_lote.all():
            lote_14_b.contratos_do_lote.remove(contrato)

        self.stdout.write(self.style.SUCCESS(f'*** Gestão de Alimentação ***'))

        self.stdout.write(self.style.SUCCESS(f'{lote_14_b.cardapio_alteracaocardapio_rastro_lote.count()} '
                                             f'alterações de cardápio passadas do Lote 14B para o 14'))
        lote_14_b.cardapio_alteracaocardapio_rastro_lote.update(rastro_lote=lote_14_a)
        self.stdout.write(self.style.SUCCESS(f'{lote_14_b.cardapio_alteracaocardapiocei_rastro_lote.count()} '
                                             f'alterações de cardápio CEI passadas do Lote 14B para o 14'))
        lote_14_b.cardapio_alteracaocardapiocei_rastro_lote.update(rastro_lote=lote_14_a)
        self.stdout.write(self.style.SUCCESS(f'{lote_14_b.cardapio_alteracaocardapiocemei_rastro_lote.count()} '
                                             f'alterações de cardápio CEMEI passadas do Lote 14B para o 14'))
        lote_14_b.cardapio_alteracaocardapiocemei_rastro_lote.update(rastro_lote=lote_14_a)
        self.stdout.write(self.style.SUCCESS(f'{lote_14_b.cardapio_gruposuspensaoalimentacao_rastro_lote.count()} '
                                             f'suspensões de alimentação passadas do Lote 14B para o 14'))
        lote_14_b.cardapio_gruposuspensaoalimentacao_rastro_lote.update(rastro_lote=lote_14_a)
        self.stdout.write(self.style.SUCCESS(f'{lote_14_b.cardapio_inversaocardapio_rastro_lote.count()} '
                                             f'inversões de cardápio passadas do Lote 14B para o 14'))
        lote_14_b.cardapio_inversaocardapio_rastro_lote.update(rastro_lote=lote_14_a)

        self.stdout.write(self.style.SUCCESS(f'{lote_14_b.cardapio_suspensaoalimentacaodacei_rastro_lote.count()} '
                                             f'suspensões de alimentação CEI passadas do Lote 14B para o 14'))
        lote_14_b.cardapio_suspensaoalimentacaodacei_rastro_lote.update(rastro_lote=lote_14_a)

        self.stdout.write(
            self.style.SUCCESS(f'{lote_14_b.inclusao_alimentacao_grupoinclusaoalimentacaonormal_rastro_lote.count()} '
                               f'inclusões de alimentação passadas do Lote 14B para o 14'))
        lote_14_b.inclusao_alimentacao_grupoinclusaoalimentacaonormal_rastro_lote.update(rastro_lote=lote_14_a)

        self.stdout.write(
            self.style.SUCCESS(f'{lote_14_b.inclusao_alimentacao_inclusaoalimentacaocontinua_rastro_lote.count()} '
                               f'inclusões de alimentação contínuas passadas do Lote 14B para o 14'))
        lote_14_b.inclusao_alimentacao_inclusaoalimentacaocontinua_rastro_lote.update(rastro_lote=lote_14_a)

        self.stdout.write(
            self.style.SUCCESS(f'{lote_14_b.inclusao_alimentacao_inclusaoalimentacaodacei_rastro_lote.count()} '
                               f'inclusões de alimentação CEI passadas do Lote 14B para o 14'))
        lote_14_b.inclusao_alimentacao_inclusaoalimentacaodacei_rastro_lote.update(rastro_lote=lote_14_a)

        self.stdout.write(
            self.style.SUCCESS(f'{lote_14_b.inclusao_alimentacao_inclusaodealimentacaocemei_rastro_lote.count()} '
                               f'inclusões de alimentação CEMEI passadas do Lote 14B para o 14'))
        lote_14_b.inclusao_alimentacao_inclusaodealimentacaocemei_rastro_lote.update(rastro_lote=lote_14_a)

        self.stdout.write(
            self.style.SUCCESS(f'{lote_14_b.inclusao_alimentacao_inclusaodealimentacaocemei_rastro_lote.count()} '
                               f'kit lanches passados do Lote 14B para o 14'))
        lote_14_b.kit_lanche_solicitacaokitlancheavulsa_rastro_lote.update(rastro_lote=lote_14_a)

        self.stdout.write(
            self.style.SUCCESS(f'{lote_14_b.kit_lanche_solicitacaokitlancheceiavulsa_rastro_lote.count()} '
                               f'kit lanches CEI passados do Lote 14B para o 14'))
        lote_14_b.kit_lanche_solicitacaokitlancheceiavulsa_rastro_lote.update(rastro_lote=lote_14_a)

        self.stdout.write(
            self.style.SUCCESS(f'{lote_14_b.kit_lanche_solicitacaokitlanchecemei_rastro_lote.count()} '
                               f'kit lanches CEMEI passados do Lote 14B para o 14'))
        lote_14_b.kit_lanche_solicitacaokitlanchecemei_rastro_lote.update(rastro_lote=lote_14_a)

        self.stdout.write(
            self.style.SUCCESS(f'{lote_14_b.kit_lanche_solicitacaokitlancheunificada_rastro_lote.count()} '
                               f'kit lanches unificados passados do Lote 14B para o 14'))
        lote_14_b.kit_lanche_solicitacaokitlancheunificada_rastro_lote.update(rastro_lote=lote_14_a)

        self.stdout.write(self.style.SUCCESS(f'*** Dieta Especial ***'))

        self.stdout.write(self.style.SUCCESS(f'{lote_14_b.dieta_especial_solicitacaodietaespecial_rastro_lote.count()} '
                                             f'solicitações de dieta especial passadas do Lote 14B para o 14'))
        lote_14_b.dieta_especial_solicitacaodietaespecial_rastro_lote.update(rastro_lote=lote_14_a)

        self.stdout.write(self.style.SUCCESS(f'Exclui o lote 14B'))
        lote_14_b.delete()
