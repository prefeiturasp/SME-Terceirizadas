from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from .serializers import DiaSobremesaDoceSerializer
from .serializers_create import DiaSobremesaDoceCreateSerializer
from ..models import DiaSobremesaDoce


class DiaSobremesaDoceViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    lookup_field = 'uuid'
    queryset = DiaSobremesaDoce.objects.all()

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return DiaSobremesaDoceCreateSerializer
        return DiaSobremesaDoceSerializer
