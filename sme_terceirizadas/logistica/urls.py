from django.urls import include, path
from rest_framework import routers

from .api.viewsets.solicitacao_remessa_viewset import ExampleView

router = routers.DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path('solicitacao-remessa', ExampleView.as_view(), name='solicitacao-remessa'),
]
