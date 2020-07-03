from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from ...escola.api.serializers import TerceirizadaSerializer, UsuarioDetalheSerializer
from ...perfil.api.serializers import UsuarioUpdateSerializer, VinculoSerializer
from ..models import Edital, Terceirizada
from .permissions import PodeCriarAdministradoresDaTerceirizada
from .serializers.serializers import EditalContratosSerializer, EditalSerializer, TerceirizadaSimplesSerializer
from .serializers.serializers_create import EditalContratosCreateSerializer, TerceirizadaCreateSerializer


class EditalViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = 'uuid'
    serializer_class = EditalSerializer
    queryset = Edital.objects.all()


class TerceirizadaViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    queryset = Terceirizada.objects.all()

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return TerceirizadaCreateSerializer
        return TerceirizadaSerializer

    @action(detail=False, methods=['GET'], url_path='lista-nomes')
    def lista_nomes(self, request):
        response = {'results': TerceirizadaSimplesSerializer(self.get_queryset(), many=True).data}
        return Response(response)


class EditalContratosViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    serializer_class = EditalContratosSerializer
    queryset = Edital.objects.all()

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return EditalContratosCreateSerializer
        return EditalContratosSerializer


class VinculoTerceirizadaViewSet(ReadOnlyModelViewSet):
    lookup_field = 'uuid'
    queryset = Terceirizada.objects.all()
    permission_classes = [PodeCriarAdministradoresDaTerceirizada]
    serializer_class = VinculoSerializer

    @action(detail=True, methods=['post'])
    def criar_equipe_administradora(self, request, uuid=None):
        try:
            terceirizada = self.get_object()
            usuario = UsuarioUpdateSerializer().create_nutricionista(terceirizada=terceirizada,
                                                                     validated_data=request.data)
            return Response(UsuarioDetalheSerializer(usuario).data)
        except serializers.ValidationError as e:
            return Response(data=dict(detail=e.args[0]), status=e.status_code)

    @action(detail=True)
    def get_equipe_administradora(self, request, uuid=None):
        terceirizada = self.get_object()
        vinculos = terceirizada.vinculos_que_podem_ser_finalizados
        return Response(self.get_serializer(vinculos, many=True).data)

    @action(detail=True, methods=['patch'])
    def finalizar_vinculo(self, request, uuid=None):
        try:
            terceirizada = self.get_object()
            vinculo_uuid = request.data.get('vinculo_uuid')
            vinculo = terceirizada.vinculos.get(uuid=vinculo_uuid)
            assert vinculo.usuario.super_admin_terceirizadas is False, 'Não pode excluir usuário Administrador'
            vinculo.finalizar_vinculo()
            return Response(self.get_serializer(vinculo).data)
        except AssertionError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
