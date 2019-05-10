from django.urls import include, path

from .api.viewsets import (
    EmailConfigurationViewSet,
)

app_name = "commom-data"
urlpatterns = [
    path("", view=EmailConfigurationViewSet, name="email"),
]
