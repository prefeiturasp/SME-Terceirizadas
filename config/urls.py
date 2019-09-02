import environ
from des import urls as des_urls
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views import defaults as default_views
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token
from rest_framework_swagger.views import get_swagger_view

from sme_pratoaberto_terceirizadas.cardapio.urls import urlpatterns as cardapio_urls
from sme_pratoaberto_terceirizadas.dados_comuns.urls import urlpatterns as comuns_urls
from sme_pratoaberto_terceirizadas.escola.urls import urlpatterns as escola_urls
from sme_pratoaberto_terceirizadas.inclusao_alimentacao.urls import urlpatterns as inclusao_urls
from sme_pratoaberto_terceirizadas.kit_lanche.urls import urlpatterns as kit_lanche_urls
from sme_pratoaberto_terceirizadas.paineis_consolidados.urls import urlpatterns as paineis_consolidados_urls
from sme_pratoaberto_terceirizadas.perfil.urls import urlpatterns as perfil_urls
from sme_pratoaberto_terceirizadas.terceirizada.urls import urlpatterns as terceirizada_urls

env = environ.Env()

schema_view = get_swagger_view(title='API de Terceirizadas', url=env.str('DJANGO_API_URL', default=''))

urlpatterns = [path('docs/', schema_view, name='docs'),
               path('django-des/', include(des_urls)),
               path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
               path(settings.ADMIN_URL, admin.site.urls),
               path("api-token-auth/", obtain_jwt_token),
               path('api-token-refresh/', refresh_jwt_token)] + static(
    settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
)

# ADDING ROUTERS FROM ALL APPS
urlpatterns += comuns_urls
urlpatterns += escola_urls
urlpatterns += perfil_urls
urlpatterns += inclusao_urls
urlpatterns += kit_lanche_urls
urlpatterns += cardapio_urls
urlpatterns += terceirizada_urls
urlpatterns += paineis_consolidados_urls

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
