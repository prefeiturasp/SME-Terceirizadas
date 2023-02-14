import pytest

pytestmark = pytest.mark.django_db


def test_unidade_medida_serializer(unidade_medida):
    from sme_terceirizadas.produto.api.serializers.serializers import UnidadeMedidaSerialzer
    serializer = UnidadeMedidaSerialzer(unidade_medida)

    assert serializer.data is not None
    assert serializer.data['uuid'] == str(unidade_medida.uuid)
    assert serializer.data['nome'] == str(unidade_medida.nome)


def test_embalagem_produto_serializer(embalagem_produto):
    from sme_terceirizadas.produto.api.serializers.serializers import EmbalagemProdutoSerialzer
    serializer = EmbalagemProdutoSerialzer(embalagem_produto)

    assert serializer.data is not None
    assert serializer.data['uuid'] == str(embalagem_produto.uuid)
    assert serializer.data['nome'] == embalagem_produto.nome


def test_marca_serializer(marca1):
    from sme_terceirizadas.produto.api.serializers.serializers import MarcaSerializer
    serializer = MarcaSerializer(marca1)

    assert serializer.data is not None
    assert serializer.data['uuid'] == str(marca1.uuid)
    assert serializer.data['nome'] == marca1.nome


def test_fabricante_serializer(fabricante):
    from sme_terceirizadas.produto.api.serializers.serializers import FabricanteSerializer
    serializer = FabricanteSerializer(fabricante)

    assert serializer.data is not None
    assert serializer.data['uuid'] == str(fabricante.uuid)
    assert serializer.data['nome'] == fabricante.nome


def test_especificacao_produto_serializer(especificacao_produto1):
    from sme_terceirizadas.produto.api.serializers.serializers import EspecificacaoProdutoSerializer
    serializer = EspecificacaoProdutoSerializer(especificacao_produto1)

    assert serializer.data is not None
    assert serializer.data['uuid'] == str(especificacao_produto1.uuid)
    assert serializer.data['volume'] == especificacao_produto1.volume


def test_produto_edital(produto_edital):
    from sme_terceirizadas.produto.api.serializers.serializers import CadastroProdutosEditalSerializer
    serializer = CadastroProdutosEditalSerializer(produto_edital)

    assert serializer.data is not None
    assert serializer.data['uuid'] == str(produto_edital.uuid)
    assert serializer.data['nome'] == produto_edital.nome
