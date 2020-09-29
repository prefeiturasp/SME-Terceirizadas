from sme_terceirizadas.perfil.models import Usuario
from sme_terceirizadas.produto.data.informacao_nutricional import data_informacao_nutricional  # noqa
from sme_terceirizadas.produto.data.protocolo_de_dieta_especial import data_protocolo_de_dieta_especial  # noqa
from sme_terceirizadas.produto.data.tipo_informacao_nutricional import data_tipo_informacao_nutricional  # noqa
from sme_terceirizadas.produto.models import InformacaoNutricional
from sme_terceirizadas.produto.models import ProtocoloDeDietaEspecial
from sme_terceirizadas.produto.models import TipoDeInformacaoNutricional
from utility.carga_dados.escola.helper import bcolors
from utility.carga_dados.helper import get_modelo
from utility.carga_dados.helper import ja_existe
from utility.carga_dados.helper import le_dados


def cria_informacao_nutricional():
    dict_tipo_nutricional = le_dados(data_tipo_informacao_nutricional)
    for item in data_informacao_nutricional:
        tipo_nutricional = get_modelo(
            modelo=TipoDeInformacaoNutricional,
            modelo_id=item.get('tipo_nutricional'),
            dicionario=dict_tipo_nutricional,
            campo_unico='nome'
        )

        data = dict(
            nome=item.get('nome'),
            tipo_nutricional=tipo_nutricional
        )
        _, created = InformacaoNutricional.objects.get_or_create(**data)
        if not created:
            ja_existe('InformacaoNutricional', item['nome'])


def cria_tipo_informacao_nutricional():
    for item in data_tipo_informacao_nutricional:
        _, created = TipoDeInformacaoNutricional.objects.get_or_create(
            nome=item['nome'])
        if not created:
            ja_existe('TipoDeInformacaoNutricional', item['nome'])


def cria_diagnosticos():
    # Protocolo de Dieta Especial
    usuario_codae = Usuario.objects.get(email='codae@admin.com')
    for item in data_protocolo_de_dieta_especial:
        obj = ProtocoloDeDietaEspecial.objects.filter(nome=item).first()
        if not obj:
            ProtocoloDeDietaEspecial.objects.create(
                nome=item,
                criado_por=usuario_codae
            )
        else:
            nome = item
            print(f'{bcolors.FAIL}Aviso: ProtocoloDeDietaEspecial: "{nome}" já existe!{bcolors.ENDC}')  # noqa
