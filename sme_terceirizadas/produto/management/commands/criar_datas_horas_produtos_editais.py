from django.core.management import BaseCommand

from sme_terceirizadas.dados_comuns.models import LogSolicitacoesUsuario
from sme_terceirizadas.produto.models import HomologacaoProduto, Produto


class Command(BaseCommand):
    help = 'Cria objetos DataHoraVinculoProdutoEdital para todos os produtos'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS(f'*** Iniciando processo de criação dos dados ***'))
        produtos = Produto.objects.filter(vinculos__isnull=False).distinct()
        for produto in produtos:
            self.cria_datas_horas_dos_vinculos_do_produto(produto)
        hom_produtos_complexos_uuids = self.produtos_complexos()
        self.lida_com_produtos_complexos(hom_produtos_complexos_uuids)
        self.stdout.write(self.style.SUCCESS(f'*** Finalizando processo de migracao de dados ***'))

    def cria_datas_horas_dos_vinculos_do_produto(self, produto):
        for produto_edital in produto.vinculos.all():
            data_hora = produto_edital.criar_data_hora_vinculo()
            data_hora.criado_em = produto_edital.criado_em
            data_hora.save()
            if produto_edital.edital.numero == 'Edital de Pregão n°78/SME/2016':
                data_hora.criado_em = produto_edital.produto.data_homologacao
                data_hora.save()

    def produtos_complexos(self):
        produtos = Produto.objects.filter(vinculos__isnull=False).distinct()
        prods_log_editais = []
        for produto in produtos:
            hom = produto.homologacao
            for log in hom.logs.all():
                if ('suspen' in log.get_status_evento_display() or
                        'não homol' in log.get_status_evento_display() or
                        'autorizou reclamação' in log.get_status_evento_display()):
                    prods_log_editais.append(hom.uuid)
                    continue
        return prods_log_editais

    def lida_com_produtos_complexos(self, hom_produtos_complexos_uuids):
        hom_produtos = HomologacaoProduto.objects.filter(uuid__in=hom_produtos_complexos_uuids)
        for hom_produto in hom_produtos:
            for log in hom_produto.logs.all():
                if log.status_evento in [
                    LogSolicitacoesUsuario.CODAE_AUTORIZOU_RECLAMACAO,
                    LogSolicitacoesUsuario.CODAE_NAO_HOMOLOGADO,
                    LogSolicitacoesUsuario.CODAE_AUTORIZOU_RECLAMACAO,
                    LogSolicitacoesUsuario.CODAE_SUSPENDEU
                ]:
                    for produto_edital in hom_produto.produto.vinculos.all():
                        data_hora_vinculo = produto_edital.criar_data_hora_vinculo(suspenso=True)
                        data_hora_vinculo.criado_em = log.criado_em
                        data_hora_vinculo.save()
