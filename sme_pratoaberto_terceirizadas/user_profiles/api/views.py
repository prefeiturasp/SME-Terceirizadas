from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView
)
from rest_framework.permissions import IsAuthenticated

from sme_pratoaberto_terceirizadas.school.models import School
from .serializers import SchoolProfileSerializer


class SchoolProfileListCreateAPIView(ListCreateAPIView):
    queryset = School.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = SchoolProfileSerializer
    lookup_field = 'eol_code'
    # Don't use Flavor.id!


class SchoolProfileRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = School.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = SchoolProfileSerializer
    lookup_field = 'eol_code'
    # Don't use Flavor.id!
