from utility.carga_dados.helper import ja_existe, progressbar

from sme_terceirizadas.perfil.data.perfis import data_perfis
from sme_terceirizadas.perfil.models import Perfil


def cria_perfis():
    for item in progressbar(data_perfis, 'Perfil'):
        _, created = Perfil.objects.get_or_create(
            nome=item['nome'],
            ativo=item['ativo'],
            super_usuario=item['super_usuario'],
        )
        if not created:
            ja_existe('Perfil', item['nome'])
