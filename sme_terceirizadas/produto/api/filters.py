from django_filters import rest_framework as filters

from ..models import Produto
from ..utils import cria_filtro_aditivos


class ProdutoFilter(filters.FilterSet):
    uuid = filters.CharFilter(field_name='homologacoes__uuid', lookup_expr='iexact')
    nome_produto = filters.CharFilter(field_name='nome', lookup_expr='icontains')
    status = filters.CharFilter(field_name='homologacoes__status__in', method='filtra_homologacoes')
    data_inicial = filters.DateFilter(field_name='homologacoes__criado_em', lookup_expr='date__gte')
    data_final = filters.DateFilter(field_name='homologacoes__criado_em', lookup_expr='date__lte')
    nome_marca = filters.CharFilter(field_name='marca__nome', lookup_expr='icontains')
    nome_fabricante = filters.CharFilter(field_name='fabricante__nome', lookup_expr='icontains')
    nome_terceirizada = filters.CharFilter(field_name='homologacoes__rastro_terceirizada__nome_fantasia',
                                           lookup_expr='icontains')
    aditivos = filters.CharFilter(field_name='aditivos', method='filtra_aditivos')

    class Meta:
        model = Produto
        fields = ['nome_produto', 'nome_marca', 'nome_fabricante', 'nome_terceirizada', 'data_inicial',
                  'data_final', 'tem_aditivos_alergenicos', 'eh_para_alunos_com_dieta']

    def filtra_aditivos(self, qs, name, value):
        filtro = cria_filtro_aditivos(value)
        qs.filter(filtro)

    def filtra_homologacoes(self, qs, name, value):
        value = self.request.query_params.getlist('status')
        filtro = {name: value}
        return qs.filter(**filtro)
