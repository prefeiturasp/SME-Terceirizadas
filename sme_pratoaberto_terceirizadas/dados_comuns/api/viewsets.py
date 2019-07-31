from des.models import DynamicEmailConfiguration
from django.db import IntegrityError
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet, ModelViewSet

from .serializers import ConfiguracaoEmailSerializer, ConfiguracaoMensagemSerializer
from ..models import ConfiguracaoMensagem
from ..models_abstract import DiasSemana, TempoPasseio
from ..utils import obter_dias_uteis_apos_hoje


class DiasDaSemanaViewSet(ViewSet):
    permission_classes = (AllowAny,)

    def list(self, request):
        return Response(dict(DiasSemana.DIAS))


class TempoDePasseioViewSet(ViewSet):
    permission_classes = (AllowAny,)

    def list(self, request):
        tempo_de_passeio_descricao = {
            TempoPasseio.QUATRO: {'quantidade_kits': 1, 'descricao': 'até 4 horas: 1 kit'},
            TempoPasseio.CINCO_A_SETE: {'quantidade_kits': 2,
                                        'descricao': 'entre 5 e 7 horas: 2 kits'},
            TempoPasseio.OITO_OU_MAIS: {'quantidade_kits': 3,
                                        'descricao': '8 ou mais horas: 3 kits'}
        }
        return Response(tempo_de_passeio_descricao)


class DiasUteisViewSet(ViewSet):
    permission_classes = (AllowAny,)

    def list(self, request):
        dias_uteis = {
            'proximos_cinco_dias_uteis': obter_dias_uteis_apos_hoje(5),
            'proximos_dois_dias_uteis': obter_dias_uteis_apos_hoje(2)
        }

        return Response(dias_uteis)


class ConfiguracaoEmailViewSet(ModelViewSet):
    queryset = DynamicEmailConfiguration.objects.all()
    serializer_class = ConfiguracaoEmailSerializer

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except IntegrityError as e:
            return Response(data={'error': 'A configuração já existe, tente usar o método PUT',
                                  'detail': '{}'.format(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ConfiguracaoMensagemViewSet(ModelViewSet):
    lookup_field = 'uuid'
    # permission_classes = [EhAdminDaCodae]
    queryset = ConfiguracaoMensagem.objects.all()
    serializer_class = ConfiguracaoMensagemSerializer
