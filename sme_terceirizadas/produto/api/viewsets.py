from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from xworkflows import InvalidTransitionError

from ...dados_comuns import constants
from ...dados_comuns.permissions import UsuarioCODAEGestaoProduto
from ..models import Fabricante, HomologacaoDoProduto, InformacaoNutricional, Marca, Produto, ProtocoloDeDietaEspecial
from .serializers.serializers import (
    FabricanteSerializer,
    FabricanteSimplesSerializer,
    HomologacaoProdutoSerializer,
    InformacaoNutricionalSerializer,
    MarcaSerializer,
    MarcaSimplesSerializer,
    ProdutoSerializer,
    ProdutoSimplesSerializer,
    ProtocoloDeDietaEspecialSerializer,
    ProtocoloSimplesSerializer, HomologacaoProdutoPainelGerencialSerializer
)
from .serializers.serializers_create import ProdutoSerializerCreate


class InformacaoNutricionalBaseViewSet(viewsets.ReadOnlyModelViewSet):

    def possui_tipo_nutricional_na_lista(self, infos_nutricionais, nome):
        tem_tipo_nutricional = False
        if len(infos_nutricionais) > 0:
            for info_nutricional in infos_nutricionais:
                if info_nutricional['nome'] == nome:
                    tem_tipo_nutricional = True
        return tem_tipo_nutricional

    def adiciona_informacao_em_tipo_nutricional(self, infos_nutricionais, objeto):
        tipo_nutricional = objeto.tipo_nutricional.nome
        for item in infos_nutricionais:
            if item['nome'] == tipo_nutricional:
                item['informacoes_nutricionais'].append({
                    'nome': objeto.nome,
                    'uuid': objeto.uuid,
                    'medida': objeto.medida
                })
        return infos_nutricionais

    def _agrupa_informacoes_por_tipo(self, query_set):
        infos_nutricionais = []
        for objeto in query_set:
            tipo_nutricional = objeto.tipo_nutricional.nome
            if self.possui_tipo_nutricional_na_lista(infos_nutricionais, tipo_nutricional):
                infos_nutricionais = self.adiciona_informacao_em_tipo_nutricional(
                    infos_nutricionais, objeto)
            else:
                info_nutricional = {
                    'nome': tipo_nutricional,
                    'informacoes_nutricionais': [{
                        'nome': objeto.nome,
                        'uuid': objeto.uuid,
                        'medida': objeto.medida
                    }]
                }
                infos_nutricionais.append(info_nutricional)
        return infos_nutricionais


class HomologacaoProdutoPainelGerencialViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    serializer_class = HomologacaoProdutoPainelGerencialSerializer
    queryset = HomologacaoDoProduto.objects.all()

    def dados_dashboard(self, query_set: list) -> dict:
        reclamacao_de_produto = query_set.filter(status=HomologacaoDoProduto.workflow_class.CODAE_AUTORIZOU_RECLAMACAO)
        suspensos = query_set.filter(status=HomologacaoDoProduto.workflow_class.CODAE_SUSPENDEU)
        correcao_de_produto = query_set.filter(status=HomologacaoDoProduto.workflow_class.CODAE_QUESTIONADO)
        aguardando_analise_reclamacao = query_set.filter(
            status=HomologacaoDoProduto.workflow_class.CODAE_PEDIU_ANALISE_RECLAMACAO)
        aguardando_analise_sensorial = query_set.filter(
            status=HomologacaoDoProduto.workflow_class.CODAE_PEDIU_ANALISE_SENSORIAL)
        pendente_homologacao = query_set.filter(status=HomologacaoDoProduto.workflow_class.CODAE_PENDENTE_HOMOLOGACAO)
        homologados = query_set.filter(status=HomologacaoDoProduto.workflow_class.CODAE_HOMOLOGADO)
        nao_homologados = query_set.filter(status=HomologacaoDoProduto.workflow_class.CODAE_NAO_HOMOLOGADO)

        sumario = {
            'Reclamação de produto': self.get_serializer(reclamacao_de_produto, many=True).data,
            'Produtos suspensos': self.get_serializer(suspensos, many=True).data,
            'Correção de produto': self.get_serializer(correcao_de_produto, many=True).data,
            'Aguardando análise de reclamação': self.get_serializer(aguardando_analise_reclamacao, many=True).data,
            'Aguardando análise sensorial': self.get_serializer(aguardando_analise_sensorial, many=True).data,
            'Pendente homologação': self.get_serializer(pendente_homologacao, many=True).data,
            'Homologados': self.get_serializer(homologados, many=True).data,
            'Não homologados': self.get_serializer(nao_homologados, many=True).data
        }

        return sumario

    def get_queryset_dashboard(self):
        query_set = self.get_queryset()
        user = self.request.user
        if user.tipo_usuario == 'terceirizada':
            query_set = query_set.filter(rastro_terceirizada=user.vinculo_atual.instituicao)
        return query_set

    @action(detail=False, methods=['GET'], url_path='dashboard')
    def dashboard(self, request):
        query_set = self.get_queryset_dashboard()
        response = {'results': self.dados_dashboard(query_set=query_set)}
        return Response(response)

    @action(detail=False, methods=['GET'], url_path='reclamacao-de-produto')
    def reclamacao_de_produto(self, request):
        query_set = self.get_queryset_dashboard()
        reclamacao_de_produto = query_set.filter(
            status=HomologacaoDoProduto.workflow_class.CODAE_AUTORIZOU_RECLAMACAO)
        response = {'results': {'Reclamação de produto': self.get_serializer(reclamacao_de_produto, many=True).data}}
        return Response(response)

    @action(detail=False, methods=['GET'], url_path='produtos-suspensos')
    def produtos_suspensos(self, request):
        query_set = self.get_queryset_dashboard()
        produtos_suspensos = query_set.filter(
            status=HomologacaoDoProduto.workflow_class.CODAE_SUSPENDEU)
        response = {'results': {'Produtos suspensos': self.get_serializer(produtos_suspensos, many=True).data}}
        return Response(response)

    @action(detail=False, methods=['GET'], url_path='correcao-de-produto')
    def correcao_de_produto(self, request):
        query_set = self.get_queryset_dashboard()
        correcao_de_produto = query_set.filter(
            status=HomologacaoDoProduto.workflow_class.CODAE_QUESTIONADO)
        response = {'results': {'Correção de produto': self.get_serializer(correcao_de_produto, many=True).data}}
        return Response(response)

    @action(detail=False, methods=['GET'], url_path='aguardando-analise-reclamacao')
    def agurdardando_analise_reclamacao(self, request):
        query_set = self.get_queryset_dashboard()
        aguardando_analise_reclamacao = query_set.filter(
            status=HomologacaoDoProduto.workflow_class.CODAE_PEDIU_ANALISE_RECLAMACAO)
        response = {
            'results': {
                'Aguardando análise reclamação': self.get_serializer(aguardando_analise_reclamacao, many=True).data
            }
        }
        return Response(response)

    @action(detail=False, methods=['GET'], url_path='aguardando-analise-sensorial')
    def agurdardando_analise_sensorial(self, request):
        query_set = self.get_queryset_dashboard()
        aguardando_analise_sensorial = query_set.filter(
            status=HomologacaoDoProduto.workflow_class.CODAE_PEDIU_ANALISE_SENSORIAL)
        response = {
            'results': {
                'Aguardando análise sensorial': self.get_serializer(aguardando_analise_sensorial, many=True).data
            }
        }
        return Response(response)

    @action(detail=False, methods=['GET'], url_path='pendente-homologacao')
    def pendente_homologacao(self, request):
        query_set = self.get_queryset_dashboard()
        pendente_homologacao = query_set.filter(
            status=HomologacaoDoProduto.workflow_class.CODAE_PENDENTE_HOMOLOGACAO)
        response = {
            'results': {
                'Pendente homologação': self.get_serializer(pendente_homologacao, many=True).data
            }
        }
        return Response(response)

    @action(detail=False, methods=['GET'], url_path='homologados')
    def homologados(self, request):
        query_set = self.get_queryset_dashboard()
        homologados = query_set.filter(status=HomologacaoDoProduto.workflow_class.CODAE_HOMOLOGADO)
        response = {'results': {'Homologados': self.get_serializer(homologados, many=True).data}}
        return Response(response)

    @action(detail=False, methods=['GET'], url_path='nao-homologados')
    def nao_homologados(self, request):
        query_set = self.get_queryset_dashboard()
        nao_homologados = query_set.filter(status=HomologacaoDoProduto.workflow_class.CODAE_NAO_HOMOLOGADO)
        response = {'results': {'Não homologados': self.get_serializer(nao_homologados, many=True).data}}
        return Response(response)


class HomologacaoProdutoViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    serializer_class = HomologacaoProdutoSerializer
    queryset = HomologacaoDoProduto.objects.all()

    @action(detail=True,
            permission_classes=(UsuarioCODAEGestaoProduto,),
            methods=['patch'],
            url_path=constants.CODAE_HOMOLOGA)
    def codae_homologa(self, request, uuid=None):
        homologacao_produto = self.get_object()
        try:
            homologacao_produto.codae_homologa(user=request.user)
            serializer = self.get_serializer(homologacao_produto)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'),
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True,
            permission_classes=(UsuarioCODAEGestaoProduto,),
            methods=['patch'],
            url_path=constants.CODAE_NAO_HOMOLOGA)
    def codae_nao_homologa(self, request, uuid=None):
        homologacao_produto = self.get_object()
        try:
            justificativa = request.data.get('justificativa', '')
            homologacao_produto.codae_nao_homologa(user=request.user, justificativa=justificativa)
            serializer = self.get_serializer(homologacao_produto)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'),
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True,
            permission_classes=(UsuarioCODAEGestaoProduto,),
            methods=['patch'],
            url_path=constants.CODAE_QUESTIONA_PEDIDO)
    def codae_questiona(self, request, uuid=None):
        homologacao_produto = self.get_object()
        try:
            justificativa = request.data.get('justificativa', '')
            homologacao_produto.codae_questiona(user=request.user, justificativa=justificativa)
            serializer = self.get_serializer(homologacao_produto)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'),
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True,
            permission_classes=(UsuarioCODAEGestaoProduto,),
            methods=['patch'],
            url_path=constants.CODAE_PEDE_ANALISE_SENSORIAL)
    def codae_pede_analise_sensorial(self, request, uuid=None):
        homologacao_produto = self.get_object()
        try:
            justificativa = request.data.get('justificativa', '')
            homologacao_produto.codae_pede_analise_sensorial(user=request.user, justificativa=justificativa)
            homologacao_produto.necessita_analise_sensorial = True
            homologacao_produto.save()
            serializer = self.get_serializer(homologacao_produto)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'),
                            status=status.HTTP_400_BAD_REQUEST)


class ProdutoViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    serializer_class = ProdutoSerializer
    queryset = Produto.objects.all()

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ProdutoSerializerCreate
        return ProdutoSerializer

    @action(detail=False, methods=['GET'], url_path='lista-nomes')
    def lista_produtos(self, request):
        query_set = Produto.objects.filter(ativo=True)
        response = {'results': ProdutoSimplesSerializer(query_set, many=True).data}
        return Response(response)

    @action(detail=False,
            methods=['GET'],
            url_path='filtro-por-nome/(?P<produto_nome>[^/.]+)')
    def filtro_por_nome(self, request, produto_nome=None):
        query_set = Produto.filtrar_por_nome(nome=produto_nome)
        page = self.paginate_queryset(query_set)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False,
            methods=['GET'],
            url_path='filtro-por-fabricante/(?P<fabricante_nome>[^/.]+)')
    def filtro_por_fabricante(self, request, fabricante_nome=None):
        query_set = Produto.filtrar_por_fabricante(nome=fabricante_nome)
        page = self.paginate_queryset(query_set)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False,
            methods=['GET'],
            url_path='filtro-por-marca/(?P<marca_nome>[^/.]+)')
    def filtro_por_marca(self, request, marca_nome=None):
        query_set = Produto.filtrar_por_marca(nome=marca_nome)
        page = self.paginate_queryset(query_set)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)


class ProtocoloDeDietaEspecialViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    serializer_class = ProtocoloDeDietaEspecialSerializer
    queryset = ProtocoloDeDietaEspecial.objects.all()

    @action(detail=False, methods=['GET'], url_path='lista-nomes')
    def lista_protocolos(self, request):
        query_set = ProtocoloDeDietaEspecial.objects.filter(ativo=True)
        response = {'results': ProtocoloSimplesSerializer(query_set, many=True).data}
        return Response(response)


class FabricanteViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    serializer_class = FabricanteSerializer
    queryset = Fabricante.objects.all()

    @action(detail=False, methods=['GET'], url_path='lista-nomes')
    def lista_fabricantes(self, request):
        query_set = Fabricante.objects.all()
        response = {'results': FabricanteSimplesSerializer(query_set, many=True).data}
        return Response(response)


class MarcaViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    serializer_class = MarcaSerializer
    queryset = Marca.objects.all()

    @action(detail=False, methods=['GET'], url_path='lista-nomes')
    def lista_marcas(self, request):
        query_set = Marca.objects.all()
        response = {'results': MarcaSimplesSerializer(query_set, many=True).data}
        return Response(response)


class InformacaoNutricionalViewSet(InformacaoNutricionalBaseViewSet):
    lookup_field = 'uuid'
    serializer_class = InformacaoNutricionalSerializer
    queryset = InformacaoNutricional.objects.all()

    @action(detail=False, methods=['GET'], url_path=f'agrupadas')
    def informacoes_nutricionais_agrupadas(self, request):
        query_set = InformacaoNutricional.objects.all()
        response = {'results': self._agrupa_informacoes_por_tipo(query_set)}
        return Response(response)
