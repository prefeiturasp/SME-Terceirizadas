from datetime import timedelta

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from ...dieta_especial.models import ClassificacaoDieta
from ..models import LancamentoDiario
from ..utils import eh_feriado_ou_fds, mes_para_faixa
from .serializers import LancamentoDiarioCreateSerializer, LancamentoDiarioSerializer


class LancamentoDiarioViewSet(ModelViewSet):
    lookup_field = 'uuid'
    queryset = LancamentoDiario.objects.all()
    serializer_class = LancamentoDiarioCreateSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return LancamentoDiarioCreateSerializer
        return LancamentoDiarioSerializer

    def create(self, request):
        grupos = ['convencional', 'grupoA', 'grupoB']

        for grupo in grupos:
            if grupo not in self.request.data:
                continue
            dados_grupo = self.request.data[grupo]
            dados_grupo['data'] = self.request.data['data_lancamento']
            dados_grupo['escola_periodo_escolar'] = self.request.data['escola_periodo_escolar']
            dados_grupo['criado_por'] = self.request.user.id
            if grupo != 'convencional':
                dados_grupo['tipo_dieta'] = ClassificacaoDieta.objects.get(nome='Tipo ' + grupo[-1]).id
            ser = LancamentoDiarioCreateSerializer(data=dados_grupo)
            ser.is_valid(raise_exception=True)
            ser.save()

        return Response('OK')

    @action(detail=False, url_path='por-mes', methods=['get'])
    def por_mes(self, request):
        (data_inicial, data_final) = mes_para_faixa(self.request.GET['mes'])
        qs = self.get_queryset().filter(
            data__range=(data_inicial, data_final),
            escola_periodo_escolar__uuid=self.request.GET['escola_periodo_escolar']
        ).all()

        datas = [data_inicial + timedelta(n) for n in range(int((data_final - data_inicial).days + 1))]
        dados_a_retornar = []

        for data in datas:
            try:
                lancamento = qs.get(data=data)
            except LancamentoDiario.DoesNotExist:
                lancamento = None
            dados_a_retornar.append({
                'dia': data.day,
                'eh_feriado_ou_fds': eh_feriado_ou_fds(data),
                'lancamento': self.get_serializer(lancamento).data if lancamento else None
            })
        return Response(dados_a_retornar)
