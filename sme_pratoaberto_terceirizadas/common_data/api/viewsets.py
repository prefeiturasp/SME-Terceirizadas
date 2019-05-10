from rest_framework.response import Response
from rest_framework.viewsets import ViewSet, ModelViewSet

from sme_pratoaberto_terceirizadas.common_data.models import EmailConfiguration
from .serializers import WorkingDaysSerializer, EmailConfigurationSerializer
from ..models import WorkingDays
from ..utils import get_working_days_after


class WorkingDaysViewSet(ViewSet):
    serializer_class = WorkingDaysSerializer

    def list(self, request):
        working_days = {
            1: WorkingDays(
                date_five_working_days=get_working_days_after(),
                date_two_working_days=get_working_days_after(2))
        }
        serializer = WorkingDaysSerializer(
            instance=working_days.values(), many=True)
        return Response(serializer.data)


class EmailConfigurationViewSet(ModelViewSet):
    queryset = EmailConfiguration.objects.all()
    serializer_class = EmailConfigurationSerializer
