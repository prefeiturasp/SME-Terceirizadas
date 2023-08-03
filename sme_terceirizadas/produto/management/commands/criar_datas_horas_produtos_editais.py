from django.core.management import BaseCommand

from sme_terceirizadas.produto.models import Produto


class Command(BaseCommand):
    help = 'Cria objetos DataHoraVinculoProdutoEdital para todos os produtos'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS(f'*** Iniciando processo de criação dos dados ***'))
        produtos = Produto.objects.filter(vinculos__isnull=False).distinct()
        for produto in produtos:
            self.stdout.write(self.style.SUCCESS(f'****************************************************************'))
            self.stdout.write(self.style.SUCCESS(f'*** Unificando homologacoes do produto: {produto.uuid} ***'))
            self.stdout.write(self.style.SUCCESS(f'*** Nome: {produto.nome} ***'))
            self.stdout.write(self.style.SUCCESS(f'*** Marca: {produto.marca.nome} ***'))
            self.stdout.write(self.style.SUCCESS(f'*** Fabricante: {produto.fabricante.nome} ***'))
            self.stdout.write(self.style.SUCCESS(f'****************************************************************'))
            self.cria_datas_horas_dos_vinculos_do_produto(produto)
        self.stdout.write(self.style.SUCCESS(f'*** Finalizando processo de migracao de dados ***'))

    def cria_datas_horas_dos_vinculos_do_produto(self, produto):
        for produto_edital in produto.vinculos.all():
            produto_edital.criar_data_hora_vinculo()
