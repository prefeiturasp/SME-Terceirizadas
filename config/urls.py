import notifications.urls
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views import defaults as default_views
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token
from rest_framework_swagger.views import get_swagger_view

from sme_pratoaberto_terceirizadas.dados_comuns.urls import urlpatterns as comuns_urls
from sme_pratoaberto_terceirizadas.escola.urls import urlpatterns as escola_urls

schema_view = get_swagger_view(title='API de Terceirizadas')

urlpatterns = [
                  path('docs', schema_view),
                  path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
                  path('inbox/notifications/', include(notifications.urls, namespace='notifications')),
                  path(settings.ADMIN_URL, admin.site.urls),
                  path("api-token-auth/", obtain_jwt_token),
                  path('api-token-refresh/', refresh_jwt_token),

              ] + static(
    settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
)

# ADDING ROUTERS FROM ALL APPS #
urlpatterns += comuns_urls
urlpatterns += escola_urls
# urlpatterns += permissions_url
# urlpatterns += user_url
# urlpatterns += common_urls
# urlpatterns += meal_kit_url
# urlpatterns += alimento_url
# urlpatterns += cardapio_url
# urlpatterns += alimentacao_url
# urlpatterns += suspensao_url

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
