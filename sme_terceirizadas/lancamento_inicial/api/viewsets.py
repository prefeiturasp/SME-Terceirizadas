from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from ...dieta_especial.models import ClassificacaoDieta
from ..models import LancamentoDiario
from .serializers import LancamentoDiarioCreateSerializer


class LancamentoDiarioViewSet(ModelViewSet):
    lookup_field = 'uuid'
    queryset = LancamentoDiario.objects.all()
    serializer_class = LancamentoDiarioCreateSerializer

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
