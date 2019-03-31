from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView
)
from rest_framework.permissions import IsAuthenticated

from .serializers import SchoolProfileSerializer
from ..models import SchoolProfile


class SchoolProfileListCreateAPIView(ListCreateAPIView):
    queryset = SchoolProfile.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = SchoolProfileSerializer
    lookup_field = 'eol_code'
    # Don't use Flavor.id!


class SchoolProfileRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = SchoolProfile.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = SchoolProfileSerializer
    lookup_field = 'eol_code'
    # Don't use Flavor.id!
