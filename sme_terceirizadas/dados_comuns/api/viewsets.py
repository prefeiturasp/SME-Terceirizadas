from des.models import DynamicEmailConfiguration
from django.db import IntegrityError
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ViewSet

from ..behaviors import DiasSemana, TempoPasseio
from ..constants import API_VERSION, TEMPO_CACHE_1H, TEMPO_CACHE_6H, obter_dias_uteis_apos_hoje
from ..models import CategoriaPerguntaFrequente, PerguntaFrequente, TemplateMensagem
from ..permissions import UsuarioCODAEGestaoAlimentacao
from .serializers import (
    CategoriaPerguntaFrequenteSerializer,
    ConfiguracaoEmailSerializer,
    ConfiguracaoMensagemSerializer,
    ConsultaPerguntasFrequentesSerializer,
    PerguntaFrequenteCreateSerializer,
    PerguntaFrequenteSerializer
)


class ApiVersion(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def list(self, request):
        return Response({'API_Version': API_VERSION})


class DiasDaSemanaViewSet(ViewSet):
    permission_classes = (AllowAny,)

    @method_decorator(cache_page(TEMPO_CACHE_6H))
    def list(self, request):
        return Response(dict(DiasSemana.DIAS))


class TempoDePasseioViewSet(ViewSet):
    permission_classes = (AllowAny,)

    @method_decorator(cache_page(TEMPO_CACHE_6H))
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

    @method_decorator(cache_page(TEMPO_CACHE_1H))
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
                                  'detail': f'{e}'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TemplateMensagemViewSet(ModelViewSet):
    lookup_field = 'uuid'
    queryset = TemplateMensagem.objects.all()
    serializer_class = ConfiguracaoMensagemSerializer


class CategoriaPerguntaFrequenteViewSet(ModelViewSet):
    lookup_field = 'uuid'
    queryset = CategoriaPerguntaFrequente.objects.all()

    def get_serializer_class(self):
        if self.action == 'perguntas_por_categoria':
            return ConsultaPerguntasFrequentesSerializer
        return CategoriaPerguntaFrequenteSerializer

    @action(detail=False, url_path='perguntas-por-categoria')
    def perguntas_por_categoria(self, request):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)


class PerguntaFrequenteViewSet(ModelViewSet):
    lookup_field = 'uuid'
    queryset = PerguntaFrequente.objects.all()

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return PerguntaFrequenteCreateSerializer
        return PerguntaFrequenteSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = (UsuarioCODAEGestaoAlimentacao,)
        return super(PerguntaFrequenteViewSet, self).get_permissions()
