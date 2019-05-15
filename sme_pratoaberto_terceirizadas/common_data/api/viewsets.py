from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from ..models import WorkingDays
from .serializers import WorkingDaysSerializer
from ..utils import get_working_days_after


class WorkingDaysViewSet(ViewSet):
    permission_classes = ()
    serializer_class = WorkingDaysSerializer

    def list(self, request):
        working_days = {
            1: WorkingDays(
                date_five_working_days=get_working_days_after().strftime('%d/%m/%Y'),
                date_two_working_days=get_working_days_after(2).strftime('%d/%m/%Y'))
        }
        serializer = WorkingDaysSerializer(
            instance=working_days.values(), many=True)
        return Response(serializer.data)
