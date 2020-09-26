from sme_terceirizadas.dados_comuns.data.contatos import data_contatos
from sme_terceirizadas.dados_comuns.data.templatemensagem import data_templatemensagem
from sme_terceirizadas.dados_comuns.models import Contato
from sme_terceirizadas.dados_comuns.models import TemplateMensagem
from utility.carga_dados.helper import ja_existe


def cria_contatos():
    for item in data_contatos:
        obj = Contato.objects.filter(email=item['email']).first()
        if not obj:
            Contato.objects.create(
                telefone=item['telefone'],
                telefone2=item['telefone2'],
                celular=item['celular'],
                email=item['email'],
            )


def cria_templatemensagem():
    for item in data_templatemensagem:
        _, created = TemplateMensagem.objects.get_or_create(
            tipo=item['tipo'],
            assunto=item['assunto'],
            template_html=item['template_html'],
        )
        if not created:
            ja_existe('TemplateMensagem', item['assunto'])
