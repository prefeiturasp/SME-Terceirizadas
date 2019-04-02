from django.conf.urls import url
from .api import views

app_name = "user_profiles"
urlpatterns = [
    # /user_profiles/api/
    # url(
    #     regex=r'^api/$',
    #     view=views.SchoolProfileListCreateAPIView.as_view(),
    #     name='user_profile_rest_api'
    # ),
    # # /user_profiles/api/:slug/
    # url(
    #     regex=r'^api/(?P<eol_code>[-\w]+)/$',
    #     view=views.SchoolProfileRetrieveUpdateDestroyAPIView.as_view(),
    #     name='user_profile_rest_api'
    # )
]
