from datetime import date

from utility.carga_dados.escola.helper import bcolors
from utility.carga_dados.helper import ja_existe, progressbar

from sme_terceirizadas.escola.models import Codae, DiretoriaRegional, Escola
from sme_terceirizadas.perfil.data.perfis import data_perfis
from sme_terceirizadas.perfil.models import Perfil, Usuario, Vinculo


def cria_perfis():
    for item in progressbar(data_perfis, 'Perfil'):
        _, created = Perfil.objects.get_or_create(
            nome=item['nome'],
            ativo=item['ativo'],
            super_usuario=item['super_usuario'],
        )
        if not created:
            ja_existe('Perfil', item['nome'])


def cria_vinculos():
    perfil = {
        'perfil_diretor_escola': Perfil.objects.get(nome='DIRETOR'),
        'perfil_diretor_escola_cei': Perfil.objects.get(nome='DIRETOR_CEI'),
        'perfil_cogestor_dre': Perfil.objects.get(nome='COGESTOR'),
        'perfil_usuario_codae': Perfil.objects.get(nome='COORDENADOR_GESTAO_ALIMENTACAO_TERCEIRIZADA'),  # noqa
        'perfil_usuario_dilog': Perfil.objects.get(nome='COORDENADOR_LOGISTICA'),  # noqa
        'perfil_usuario_nutri_codae': Perfil.objects.get(nome='COORDENADOR_DIETA_ESPECIAL'),  # noqa
        'perfil_usuario_nutri_supervisao': Perfil.objects.get(nome='COORDENADOR_SUPERVISAO_NUTRICAO'),  # noqa
        'perfil_coordenador_gestao_produto': Perfil.objects.get(nome='COORDENADOR_GESTAO_PRODUTO'),  # noqa
        'perfil_usuario_terceirizada': Perfil.objects.get(nome='NUTRI_ADMIN_RESPONSAVEL'),  # noqa
    }

    usuario = {
        'usuario_escola': Usuario.objects.get(email='escola@admin.com'),
        'usuario_escola_cei': Usuario.objects.get(email='escolacei@admin.com'),
        'usuario_escola_cei_ceu': Usuario.objects.get(email='escolaceiceu@admin.com'),
        'usuario_escola_cci': Usuario.objects.get(email='escolacci@admin.com'),
        'usuario_escola_emef': Usuario.objects.get(email='escolaemef@admin.com'),
        'usuario_escola_emebs': Usuario.objects.get(email='escolaemebs@admin.com'),
        'usuario_escola_cieja': Usuario.objects.get(email='escolacieja@admin.com'),
        'usuario_escola_emei': Usuario.objects.get(email='escolaemei@admin.com'),
        'usuario_escola_ceu_emei': Usuario.objects.get(email='escolaceuemei@admin.com'),
        'usuario_escola_ceu_emef': Usuario.objects.get(email='escolaceuemef@admin.com'),
        'usuario_dre': Usuario.objects.get(email='dre@admin.com'),
        'usuario_codae': Usuario.objects.get(email='codae@admin.com'),
        'usuario_dilog': Usuario.objects.get(email='dilog@admin.com'),
        'usuario_nutri_codae': Usuario.objects.get(email='nutricodae@admin.com'),
        'usuario_nutri_supervisao': Usuario.objects.get(email='nutrisupervisao@admin.com'),
        'usuario_gestao_produto_codae': Usuario.objects.get(email='gpcodae@admin.com'),
        'usuario_terceirizada': Usuario.objects.get(email='terceirizada@admin.com'),
    }

    items = [
        {
            'nome': 'EMEF JOSE ERMIRIO DE MORAIS, SEN.',
            'perfil': perfil['perfil_diretor_escola'],
            'usuario': usuario['usuario_escola'],
        },
        {
            'nome': 'CEI ENEDINA DE SOUSA CARVALHO',
            'perfil': perfil['perfil_diretor_escola_cei'],
            'usuario': usuario['usuario_escola_cei'],
        },
        {
            'nome': 'CEI CEU MENINOS',
            'perfil': perfil['perfil_diretor_escola_cei'],
            'usuario': usuario['usuario_escola_cei_ceu'],
        },
        {
            'nome': 'CCI CAMARA MUNICIPAL DE SAO PAULO',
            'perfil': perfil['perfil_diretor_escola_cei'],
            'usuario': usuario['usuario_escola_cci'],
        },
        {
            'nome': 'EMEF PERICLES EUGENIO DA SILVA RAMOS',
            'perfil': perfil['perfil_diretor_escola'],
            'usuario': usuario['usuario_escola_emef'],
        },
        {
            'nome': 'EMEBS HELEN KELLER',
            'perfil': perfil['perfil_diretor_escola'],
            'usuario': usuario['usuario_escola_emebs'],
        },
        {
            'nome': 'CIEJA CLOVIS CAITANO MIQUELAZZO - IPIRANGA',
            'perfil': perfil['perfil_diretor_escola'],
            'usuario': usuario['usuario_escola_cieja'],
        },
        {
            'nome': 'EMEI SENA MADUREIRA',
            'perfil': perfil['perfil_diretor_escola'],
            'usuario': usuario['usuario_escola_emei'],
        },
        {
            'nome': 'CEU EMEI BENNO HUBERT STOLLENWERK, PE.',
            'perfil': perfil['perfil_diretor_escola'],
            'usuario': usuario['usuario_escola_ceu_emei'],
        },
        {
            'nome': 'CEU EMEF MARA CRISTINA TATAGLIA SENA, PROFA.',
            'perfil': perfil['perfil_diretor_escola'],
            'usuario': usuario['usuario_escola_ceu_emef'],
        },
    ]

    data_atual = date.today()

    for item in progressbar(items, 'Perfil'):
        escola = Escola.objects.get(nome=item['nome'])
        vinculo = Vinculo.objects.filter(
            perfil=item['perfil'],
            usuario=item['usuario'],
        )
        if vinculo.first():
            print(f'{bcolors.FAIL}Vinculo já existe.{bcolors.ENDC}')
        else:
            Vinculo.objects.create(
                instituicao=escola,
                perfil=item['perfil'],
                usuario=item['usuario'],
                data_inicial=data_atual
            )

    diretoria_regional = DiretoriaRegional.objects.get(nome='DIRETORIA REGIONAL DE EDUCACAO IPIRANGA')  # noqa
    codae_alimentacao, created = Codae.objects.get_or_create(nome='CODAE - GESTAO ALIMENTAÇÃO')
    dilog, created = Codae.objects.get_or_create(nome='CODAE - DILOG')
    codae_dieta_especial, created = Codae.objects.get_or_create(nome='CODAE - GESTÃO DIETA ESPECIAL')
    codae_produtos, created = Codae.objects.get_or_create(nome='CODAE - GESTÃO PRODUTOS')
    codae_nutrisupervisao, created = Codae.objects.get_or_create(nome='CODAE - SUPERVISÃO DE NUTRIÇÃO')
    escola = Escola.objects.get(nome='EMEF JOSE ERMIRIO DE MORAIS, SEN.')  # noqa
    terceirizada = escola.lote.terceirizada

    items_especificos = [
        {
            'instituicao': diretoria_regional,
            'perfil': perfil['perfil_cogestor_dre'],
            'usuario': usuario['usuario_dre'],
        },
        {
            'instituicao': codae_alimentacao,
            'perfil': perfil['perfil_usuario_codae'],
            'usuario': usuario['usuario_codae'],
        },
        {
            'instituicao': dilog,
            'perfil': perfil['perfil_usuario_dilog'],
            'usuario': usuario['usuario_dilog'],
        },
        {
            'instituicao': codae_dieta_especial,
            'perfil': perfil['perfil_usuario_nutri_codae'],
            'usuario': usuario['usuario_nutri_codae'],
        },
        {
            'instituicao': codae_nutrisupervisao,
            'perfil': perfil['perfil_usuario_nutri_supervisao'],
            'usuario': usuario['usuario_nutri_supervisao'],
        },
        {
            'instituicao': codae_produtos,
            'perfil': perfil['perfil_coordenador_gestao_produto'],
            'usuario': usuario['usuario_gestao_produto_codae'],
        },
        {
            'instituicao': terceirizada,
            'perfil': perfil['perfil_usuario_terceirizada'],
            'usuario': usuario['usuario_terceirizada'],
        },
    ]

    for item in progressbar(items_especificos, 'Perfil especifico'):
        vinculo = Vinculo.objects.filter(
            perfil=item['perfil'],
            usuario=item['usuario'],
        )
        if vinculo.first():
            print(f'{bcolors.FAIL}Vinculo já existe.{bcolors.ENDC}')
        else:
            Vinculo.objects.create(
                instituicao=item['instituicao'],
                perfil=item['perfil'],
                usuario=item['usuario'],
                data_inicial=data_atual,
            )
