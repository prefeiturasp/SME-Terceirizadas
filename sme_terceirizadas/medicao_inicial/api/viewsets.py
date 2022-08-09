from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from ...dados_comuns.permissions import ViewSetActionPermissionMixin
from ...escola.api.permissions import PodeCriarAdministradoresDaCODAEGestaoAlimentacaoTerceirizada
from ..models import DiaSobremesaDoce
from .permissions import EhAdministradorMedicaoInicialOuGestaoAlimentacao
from .serializers import DiaSobremesaDoceSerializer
from .serializers_create import DiaSobremesaDoceCreateManySerializer


class DiaSobremesaDoceViewSet(ViewSetActionPermissionMixin, ModelViewSet):
    permission_action_classes = {
        'list': [EhAdministradorMedicaoInicialOuGestaoAlimentacao],
        'create': [PodeCriarAdministradoresDaCODAEGestaoAlimentacaoTerceirizada],
        'delete': [PodeCriarAdministradoresDaCODAEGestaoAlimentacaoTerceirizada]
    }
    queryset = DiaSobremesaDoce.objects.all()
    lookup_field = 'uuid'

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return DiaSobremesaDoceCreateManySerializer
        return DiaSobremesaDoceSerializer

    def get_queryset(self):
        queryset = DiaSobremesaDoce.objects.all()
        if 'mes' in self.request.query_params and 'ano' in self.request.query_params:
            queryset = queryset.filter(data__month=self.request.query_params.get('mes'),
                                       data__year=self.request.query_params.get('ano'))
        return queryset

    def create(self, request, *args, **kwargs):
        try:
            return super(DiaSobremesaDoceViewSet, self).create(request, *args, **kwargs)
        except AssertionError as error:
            if str(error) == '`create()` did not return an object instance.':
                return Response(status=status.HTTP_201_CREATED)
            return Response({'detail': str(error)}, status=status.HTTP_400_BAD_REQUEST)
