from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from sme_pratoaberto_terceirizadas.escola.models import Escola
from sme_pratoaberto_terceirizadas.escola.api.serializers import EscolaSerializer, PeriodoEscolarSerializer


class EscolaViewSet(ModelViewSet):
    """
    Endpoint para Escolas
    """
    queryset = Escola.objects.all()
    serializer_class = EscolaSerializer
    object_class = Escola

    @action(detail=False, methods=['get'])
    def get_periodos(self, request):
        response = {'content': {}, 'log_content': {}, 'code': None}
        try:
            usuario = request.user
            escola = get_object_or_404(Escola, users=usuario)
            periodos_escolares = escola.periodos.all().order_by('nome')
        except Http404 as error:
            response['log_content'] = [_('usuario nao encontrado')] if 'User' in str(error) else [_('escola nao encontrada')]
            response['code'] = status.HTTP_404_NOT_FOUND
        except Exception as e:
            print(e)
            response['code'] = status.HTTP_400_BAD_REQUEST
        else:
            response['code'] = status.HTTP_200_OK
            response['content']['periodos_escolares'] = PeriodoEscolarSerializer(periodos_escolares, many=True).data
        return Response(response, status=response['code'])
