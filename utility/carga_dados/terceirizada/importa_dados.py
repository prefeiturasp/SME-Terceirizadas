from utility.carga_dados.helper import ja_existe, progressbar

from sme_terceirizadas.terceirizada.data.contratos import data_contratos
from sme_terceirizadas.terceirizada.data.editais import data_editais
from sme_terceirizadas.terceirizada.data.nutricionistas import data_nutricionistas
from sme_terceirizadas.terceirizada.data.terceirizadas import data_terceirizadas
from sme_terceirizadas.terceirizada.data.vigencias import data_vigencias
from sme_terceirizadas.terceirizada.models import Contrato, Edital, Nutricionista, Terceirizada, VigenciaContrato


def cria_edital():
    for item in progressbar(data_editais, 'Edital'):
        _, created = Edital.objects.get_or_create(
            numero=item['numero'],
            tipo_contratacao=item['tipo_contratacao'],
            processo=item['processo'],
            objeto=item['objeto'],
        )
        if not created:
            ja_existe('Edital', item['numero'])


def cria_terceirizadas():
    for item in progressbar(data_terceirizadas, 'Terceirizada'):
        _, created = Terceirizada.objects.get_or_create(
            cnpj=item['cnpj'],
            nome_fantasia=item['nome_fantasia'],
            razao_social=item['razao_social'],
            representante_legal=item['representante_legal'],
            representante_telefone=item['representante_telefone'],
            representante_email=item['representante_email'],
        )
        if not created:
            ja_existe('Terceirizada', item['cnpj'])
