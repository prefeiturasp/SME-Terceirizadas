from django.urls import path

from .api.viewsets import (
    EmailConfigurationViewSet,
)
from .views import send_test_email

app_name = "commom-data"
urlpatterns = [
    # path("", view=EmailConfigurationViewSet, name="email"),
    path(r"test", view=send_test_email, name="test_email"),
]
