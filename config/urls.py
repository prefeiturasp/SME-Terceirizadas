import environ
from des import urls as des_urls
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views import defaults as default_views
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token
from rest_framework_swagger.views import get_swagger_view

from sme_terceirizadas.cardapio.urls import urlpatterns as cardapio_urls
from sme_terceirizadas.dados_comuns.urls import urlpatterns as comuns_urls
from sme_terceirizadas.dieta_especial.urls import urlpatterns as dieta_especial_urls
from sme_terceirizadas.eol_servico.urls import urlpatterns as eol_servico_urls
from sme_terceirizadas.escola.urls import urlpatterns as escola_urls
from sme_terceirizadas.inclusao_alimentacao.urls import urlpatterns as inclusao_urls
from sme_terceirizadas.kit_lanche.urls import urlpatterns as kit_lanche_urls
from sme_terceirizadas.lancamento_inicial.urls import urlpatterns as lancamento_inicial_urls
from sme_terceirizadas.logistica.urls import urlpatterns as logistica_urls
from sme_terceirizadas.paineis_consolidados.urls import urlpatterns as paineis_consolidados_urls
from sme_terceirizadas.perfil.urls import urlpatterns as perfil_urls
from sme_terceirizadas.produto.urls import urlpatterns as produto_urls
from sme_terceirizadas.relatorios.urls import urlpatterns as relatorio_urls
from sme_terceirizadas.terceirizada.urls import urlpatterns as terceirizada_urls

env = environ.Env()

schema_view = get_swagger_view(title='API de Terceirizadas', url=env.str('DJANGO_API_URL', default=''))

urlpatterns = [path('docs/', schema_view, name='docs'),
               path('django-des/', include(des_urls)),
               path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
               path(settings.ADMIN_URL, admin.site.urls),
               path('api-token-auth/', obtain_jwt_token),
               path('api-token-refresh/', refresh_jwt_token),
               path('', include('django_prometheus.urls')),
               ] + static(
    settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
)

# ADDING ROUTERS FROM ALL APPS
urlpatterns += comuns_urls
urlpatterns += eol_servico_urls
urlpatterns += escola_urls
urlpatterns += perfil_urls
urlpatterns += inclusao_urls
urlpatterns += kit_lanche_urls
urlpatterns += lancamento_inicial_urls
urlpatterns += cardapio_urls
urlpatterns += terceirizada_urls
urlpatterns += paineis_consolidados_urls
urlpatterns += dieta_especial_urls
urlpatterns += relatorio_urls
urlpatterns += produto_urls
urlpatterns += logistica_urls

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            '400/',
            default_views.bad_request,
            kwargs={'exception': Exception('Bad Request!')},
        ),
        path(
            '403/',
            default_views.permission_denied,
            kwargs={'exception': Exception('Permission Denied')},
        ),
        path(
            '404/',
            default_views.page_not_found,
            kwargs={'exception': Exception('Page not Found')},
        ),
        path('500/', default_views.server_error),
    ]
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path('__debug__/', include(debug_toolbar.urls))] + urlpatterns
