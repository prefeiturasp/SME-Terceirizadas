from sme_terceirizadas.produto.data.informacao_nutricional import data_informacao_nutricional
from sme_terceirizadas.produto.data.tipo_informacao_nutricional import data_tipo_informacao_nutricional
from sme_terceirizadas.produto.models import TipoDeInformacaoNutricional
from sme_terceirizadas.produto.models import InformacaoNutricional
from utility.carga_dados.helper import ja_existe


def cria_informacao_nutricional():
    pass


def cria_tipo_informacao_nutricional():
    for item in data_tipo_informacao_nutricional:
        _, created = TipoDeInformacaoNutricional.objects.get_or_create(
            nome=item['nome'])
        if not created:
            ja_existe('TipoDeInformacaoNutricional', item['nome'])
