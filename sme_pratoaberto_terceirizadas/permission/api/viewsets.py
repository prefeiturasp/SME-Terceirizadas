from rest_framework import viewsets
from ..models import Permission
from .serializers import ProfileSerializer


class PermissionViewSets(viewsets.ModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = ProfileSerializer

    def list(self, request, *args, **kwargs):
        print(request)
        return super(PermissionViewSets, self).list(request, *args, **kwargs)
