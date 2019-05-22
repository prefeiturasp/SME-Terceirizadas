from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from sme_pratoaberto_terceirizadas.school.models import School
from sme_pratoaberto_terceirizadas.users.models import User
from sme_pratoaberto_terceirizadas.school.api.serializers import SchoolSerializer, SchoolPeriodSerializer


class SchoolViewSet(ModelViewSet):
    """
    Endpoint para Escolas
    """
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
    object_class = School
    permission_classes = ()

    @action(methods=['get'], permission_classes=[], detail=True)
    def get_periods(self, request, pk=None):
        response = {'content': {}, 'log_content': {}, 'code': None}
        try:
            user = get_object_or_404(User, uuid=pk)
            school = get_object_or_404(School, users=user)
            school_periods = school.periods.all().order_by('name')
        except Http404 as error:
            response['log_content'] = [_('user not found')] if 'User' in str(error) else [_('school not found')]
            response['code'] = status.HTTP_404_NOT_FOUND
        except Exception as e:
            print(e)
            response['code'] = status.HTTP_400_BAD_REQUEST
        else:
            response['code'] = status.HTTP_200_OK
            response['content']['school_periods'] = SchoolPeriodSerializer(school_periods, many=True).data
        return Response(response, status=response['code'])
