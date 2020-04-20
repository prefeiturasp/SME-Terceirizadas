from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import (
    Fabricante,
    InformacaoNutricional,
    Marca,
    Produto,
    ProtocoloDeDietaEspecial,
)

from .serializers.serializers import (
    ProdutoSerializer, InformacaoNutricionalSerializer, FabricanteSerializer, MarcaSerializer,
    ProtocoloDeDietaEspecialSerializer
)

from .serializers.serializers_create import (
    ProdutoSerializerCreate
)


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
                    'uuid': objeto.uuid
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
                        'uuid': objeto.uuid
                    }]
                }
                infos_nutricionais.append(info_nutricional)
        return infos_nutricionais


class ProdutoViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    serializer_class = ProdutoSerializer
    queryset = Produto.objects.all()

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ProdutoSerializerCreate
        return ProdutoSerializer


class ProtocoloDeDietaEspecialViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    serializer_class = ProtocoloDeDietaEspecialSerializer
    queryset = ProtocoloDeDietaEspecial.objects.all()


class FabricanteViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    serializer_class = FabricanteSerializer
    queryset = Fabricante.objects.all()


class MarcaViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    serializer_class = MarcaSerializer
    queryset = Marca.objects.all()


class InformacaoNutricionalViewSet(InformacaoNutricionalBaseViewSet):
    lookup_field = 'uuid'
    serializer_class = InformacaoNutricionalSerializer
    queryset = InformacaoNutricional.objects.all()

    @action(detail=False, methods=['GET'], url_path=f'agrupadas')
    def informacoes_nutricionais_agrupadas(self, request):
        query_set = InformacaoNutricional.objects.all()
        response = {'results': self._agrupa_informacoes_por_tipo(query_set)}
        return Response(response)
