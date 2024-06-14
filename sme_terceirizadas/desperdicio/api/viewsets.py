from rest_framework import viewsets
from rest_framework.response import Response

from ..models import Classificacao
from .serializers.serializers import (
    ClassificacaoSerializer,
    ClassificacaoCreateSerializer
)  

class ClassificacaoViewSet(viewsets.ModelViewSet):
    lookup_field = "uuid"
    queryset = Classificacao.objects.all()

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return ClassificacaoCreateSerializer
        return ClassificacaoSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        serializer = self.get_serializer(queryset, many=True)
        return Response({"results": serializer.data})

    def get_queryset(self):
        qs = Classificacao.objects.all().order_by("tipo", "valor")        

        return qs.distinct()