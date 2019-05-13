from django.urls import path, include
from rest_framework import routers

from .api import viewsets
from .views import send_test_email

router = routers.DefaultRouter()
router.register('email', viewsets.EmailConfigurationViewSet)

urlpatterns = [
    path("api/v1/", include(router.urls)),
    path("api/v1/email-test/", send_test_email, name="send_test_email")
]
