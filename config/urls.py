import notifications.urls
from des import urls as des_urls
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.utils.translation import ugettext as _
from django.views import defaults as default_views
from rest_framework.routers import DefaultRouter
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token
from rest_framework_swagger.views import get_swagger_view

from sme_pratoaberto_terceirizadas.cardapio.urls import urlpatterns as cardapio_url
from sme_pratoaberto_terceirizadas.common_data.api.viewsets import WorkingDaysViewSet
from sme_pratoaberto_terceirizadas.common_data.urls import urlpatterns as common_urls
from sme_pratoaberto_terceirizadas.alimento.api.routers import urlpatterns as alimento_url
from sme_pratoaberto_terceirizadas.food_inclusion.api.viewsets import FoodInclusionViewSet
from sme_pratoaberto_terceirizadas.meal_kit.api.routers import urlpatterns as meal_kit_url
from sme_pratoaberto_terceirizadas.permission.routers import urlpatterns as permissions_url
from sme_pratoaberto_terceirizadas.escola.routers import urlpatterns as escola_url
from sme_pratoaberto_terceirizadas.users.routers import urlpatterns as user_url
from sme_pratoaberto_terceirizadas.alimentacao.api.routers import urlpattern as alimentacao_url
from sme_pratoaberto_terceirizadas.suspensao_de_alimentacao.api.routers import urlpatterns as suspensao_url

schema_view = get_swagger_view(title=_('API of SME-Companies'))

route = DefaultRouter(trailing_slash=True)
route.register('working_days', WorkingDaysViewSet, 'working_days')
route.register('food_inclusion', FoodInclusionViewSet)

urlpatterns = [
                  path('docs', schema_view),
                  path('', include(route.urls)),
                  path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
                  path('inbox/notifications/', include(notifications.urls, namespace='notifications')),
                  path(settings.ADMIN_URL, admin.site.urls),
                  path("api-token-auth/", obtain_jwt_token),
                  path('api-token-refresh/', refresh_jwt_token),
                  path('django-des/', include(des_urls)),

              ] + static(
    settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
)

# ADDING ROUTERS FROM ALL APPS ####
urlpatterns += permissions_url
urlpatterns += escola_url
urlpatterns += user_url
urlpatterns += common_urls
urlpatterns += meal_kit_url
urlpatterns += alimento_url
urlpatterns += cardapio_url
urlpatterns += alimentacao_url
urlpatterns += suspensao_url

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
