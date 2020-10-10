from random import choice, randint, random
from utility.carga_dados.escola.helper import bcolors
from utility.carga_dados.helper import get_modelo, ja_existe, le_dados, progressbar

from sme_terceirizadas.dados_comuns.fluxo_status import HomologacaoProdutoWorkflow
from sme_terceirizadas.dados_comuns.models import LogSolicitacoesUsuario
from sme_terceirizadas.perfil.models import Usuario
from sme_terceirizadas.produto.data.informacao_nutricional import data_informacao_nutricional  # noqa
from sme_terceirizadas.produto.data.protocolo_de_dieta_especial import data_protocolo_de_dieta_especial  # noqa
from sme_terceirizadas.produto.data.tipo_informacao_nutricional import data_tipo_informacao_nutricional  # noqa
from sme_terceirizadas.produto.data.produtos import data_produtos
from sme_terceirizadas.produto.models import (
    Fabricante,
    HomologacaoDoProduto,
    InformacaoNutricional,
    Marca,
    Produto,
    ProtocoloDeDietaEspecial,
    TipoDeInformacaoNutricional,
)
from faker import Faker

faker = Faker()
fake = Faker('pt-br')


def cria_informacao_nutricional():
    dict_tipo_nutricional = le_dados(data_tipo_informacao_nutricional)
    for item in progressbar(data_informacao_nutricional, 'Informacao Nutricional'):  # noqa
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
    for item in progressbar(data_tipo_informacao_nutricional, 'Tipo de Informacao Nutricional'):  # noqa
        _, created = TipoDeInformacaoNutricional.objects.get_or_create(
            nome=item['nome'])
        if not created:
            ja_existe('TipoDeInformacaoNutricional', item['nome'])


def cria_diagnosticos():
    # Protocolo de Dieta Especial
    usuario_codae = Usuario.objects.get(email='codae@admin.com')
    for item in progressbar(data_protocolo_de_dieta_especial, 'Protocolo de Dieta Especial'):  # noqa
        obj = ProtocoloDeDietaEspecial.objects.filter(nome=item).first()
        if not obj:
            ProtocoloDeDietaEspecial.objects.create(
                nome=item,
                criado_por=usuario_codae
            )
        else:
            nome = item
            print(f'{bcolors.FAIL}Aviso: ProtocoloDeDietaEspecial: "{nome}" já existe!{bcolors.ENDC}')  # noqa


def cria_marca():
    # Deleta produtos e marcas.
    Produto.objects.all().delete()
    Marca.objects.all().delete()
    # Cria marcas novas.
    for _ in progressbar(range(20), 'Marca'):
        nome = faker.company().split()[0].replace(',', '').split('-')[0]
        Marca.objects.create(nome=nome)


def cria_fabricante():
    Fabricante.objects.all().delete()
    for _ in progressbar(range(20), 'Fabricante'):
        nome = fake.company()
        Fabricante.objects.create(nome=nome)


def cria_homologacao_do_produto_passo_01(produto):
    criado_por = Usuario.objects.get(email='terceirizada@admin.com')
    # Se não colocar o 'rastro_terceirizada'
    # ele não mostra os produtos no dashboard.
    rastro_terceirizada = criado_por.vinculo_atual.instituicao
    homologacao_do_produto = HomologacaoDoProduto.objects.create(
        criado_por=criado_por,
        produto=produto,
        status='CODAE_PENDENTE_HOMOLOGACAO',
        rastro_terceirizada=rastro_terceirizada
    )

    # Monta um dicionário dos STATUS_POSSIVEIS
    _status = LogSolicitacoesUsuario.STATUS_POSSIVEIS
    status = {v: k for (k, v) in _status}

    _tipos = LogSolicitacoesUsuario.TIPOS_SOLICITACOES
    tipos = {v: k for (k, v) in _tipos}

    LogSolicitacoesUsuario.objects.create(
        descricao=homologacao_do_produto,
        justificativa='Lorem',
        status_evento=status['Solicitação Realizada'],
        solicitacao_tipo=tipos['Homologação de Produto'],
        usuario=criado_por,
        uuid_original=homologacao_do_produto.uuid,
    )


def cria_produto():
    for item in progressbar(data_produtos, 'Produto'):
        marcas = Marca.objects.all()
        marca = choice([item for item in marcas])

        fabricantes = Fabricante.objects.all()
        fabricante = choice([item for item in fabricantes])

        componentes = fake.sentence(nb_words=5)
        aditivos = fake.sentence(nb_words=10)
        tipo = fake.word()
        embalagem = fake.word()
        prazo_validade = faker.date_this_year()
        info_armazenamento = fake.sentence(nb_words=5)
        outras_informacoes = fake.sentence(nb_words=10)
        numero_registro = faker.bothify(letters='ABCDEFGHIJ')
        porcao = str(randint(50, 300)) + str(choice([' g', ' ml']))
        unidade_caseira = str(round(randint(1, 5) * random(), 2)).replace('.', ',') + ' unidade'  # noqa

        produto = Produto.objects.create(
            nome=item,
            marca=marca,
            fabricante=fabricante,
            componentes=componentes,
            aditivos=aditivos,
            tipo=tipo,
            embalagem=embalagem,
            prazo_validade=prazo_validade,
            info_armazenamento=info_armazenamento,
            outras_informacoes=outras_informacoes,
            numero_registro=numero_registro,
            porcao=porcao,
            unidade_caseira=unidade_caseira,
        )
        cria_homologacao_do_produto_passo_01(produto)


def cria_homologacao_do_produto():
    # Não utilizado no momento..
    # Percorre os status de homologação
    criado_por = Usuario.objects.get(email='terceirizada@admin.com')
    for status in HomologacaoProdutoWorkflow.states:
        produto = Produto.objects.first()
        HomologacaoDoProduto.objects.create(
            criado_por=criado_por,
            produto=produto,
            status=status,
            rastro_terceirizada=criado_por.vinculo_atual.instituicao
        )
