from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from xworkflows import InvalidTransitionError

from .permissions import (
    PodeAprovarAlimentacaoContinuaDaEscolaPermission, PodeIniciarInclusaoAlimentacaoContinuaPermission
)
from .serializers import serializers, serializers_create
from ..models import (
    GrupoInclusaoAlimentacaoNormal, InclusaoAlimentacaoContinua,
    MotivoInclusaoContinua,
    MotivoInclusaoNormal
)
from ...dados_comuns import constants


class MotivoInclusaoContinuaViewSet(ReadOnlyModelViewSet):
    lookup_field = 'uuid'
    queryset = MotivoInclusaoContinua.objects.all()
    serializer_class = serializers.MotivoInclusaoContinuaSerializer


class MotivoInclusaoNormalViewSet(ReadOnlyModelViewSet):
    lookup_field = 'uuid'
    queryset = MotivoInclusaoNormal.objects.all()
    serializer_class = serializers.MotivoInclusaoNormalSerializer


class GrupoInclusaoAlimentacaoNormalViewSet(ModelViewSet):
    lookup_field = 'uuid'
    queryset = GrupoInclusaoAlimentacaoNormal.objects.all()
    serializer_class = serializers.GrupoInclusaoAlimentacaoNormalSerializer

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return serializers_create.GrupoInclusaoAlimentacaoNormalCreationSerializer
        return serializers.GrupoInclusaoAlimentacaoNormalSerializer

    @action(detail=False, url_path=constants.SOLICITACOES_DO_USUARIO)
    def minhas_solicitacoes(self, request):
        usuario = request.user
        alimentacoes_normais = GrupoInclusaoAlimentacaoNormal.get_solicitacoes_rascunho(usuario)
        page = self.paginate_queryset(alimentacoes_normais)
        serializer = serializers.GrupoInclusaoAlimentacaoNormalSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False,
            url_path=f'{constants.PEDIDOS_CODAE}/{constants.FILTRO_PADRAO_PEDIDOS}')
    def pedidos_codae(self, request, filtro_aplicado='sem_filtro'):
        # TODO: colocar regras de codae CODAE aqui...
        usuario = request.user
        # TODO: aguardando definição de perfis pra saber
        codae = usuario.CODAE.first()
        inclusoes_continuas = codae.grupos_inclusoes_alimentacao_normal_das_minhas_escolas(
            filtro_aplicado
        )
        page = self.paginate_queryset(inclusoes_continuas)
        serializer = serializers.GrupoInclusaoAlimentacaoNormalSimplesSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False,
            url_path='pedidos-prioritarios-diretoria-regional/'
                     '(?P<filtro_aplicado>(sem_filtro|hoje|daqui_a_7_dias|daqui_a_30_dias)+)')
    def pedidos_prioritarios_diretoria_regional(self, request, filtro_aplicado='sem_filtro'):
        usuario = request.user
        # TODO: aguardando definição de perfis pra saber em qual DRE eu estou fazendo a requisição
        diretoria_regional = usuario.diretorias_regionais.first()
        inclusoes_normais = diretoria_regional.inclusoes_normais_das_minhas_escolas_no_prazo_vencendo(
            filtro_aplicado
        )
        page = self.paginate_queryset(inclusoes_normais)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False,
            url_path='pedidos-no-limite-diretoria-regional/'
                     '(?P<filtro_aplicado>(sem_filtro|daqui_a_7_dias|daqui_a_30_dias)+)')
    def pedidos_no_limite_diretoria_regional(self, request, filtro_aplicado='sem_filtro'):
        usuario = request.user
        # TODO: aguardando definição de perfis pra saber em qual DRE eu estou fazendo a requisição
        diretoria_regional = usuario.diretorias_regionais.first()
        inclusoes_normais = diretoria_regional.inclusoes_normais_das_minhas_escolas_no_prazo_limite(
            filtro_aplicado
        )
        page = self.paginate_queryset(inclusoes_normais)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False,
            url_path='pedidos-no-prazo-diretoria-regional/'
                     '(?P<filtro_aplicado>(sem_filtro|daqui_a_7_dias|daqui_a_30_dias)+)')
    def pedidos_no_prazo_diretoria_regional(self, request, filtro_aplicado='sem_filtro'):
        usuario = request.user
        # TODO: aguardando definição de perfis pra saber em qual DRE eu estou fazendo a requisição
        diretoria_regional = usuario.diretorias_regionais.first()
        inclusoes_normais = diretoria_regional.inclusoes_normais_das_minhas_escolas_no_prazo_regular(
            filtro_aplicado
        )
        page = self.paginate_queryset(inclusoes_normais)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path='pedidos-aprovados-diretoria-regional')
    def pedidos_aprovados_diretoria_regional(self, request):
        usuario = request.user
        # TODO: aguardando definição de perfis pra saber em qual DRE eu estou fazendo a requisição
        diretoria_regional = usuario.diretorias_regionais.first()
        inclusoes_normais = diretoria_regional.inclusoes_normais_aprovadas
        page = self.paginate_queryset(inclusoes_normais)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path='pedidos-reprovados-diretoria-regional')
    def pedidos_reprovados_diretoria_regional(self, request):
        usuario = request.user
        # TODO: aguardando definição de perfis pra saber em qual DRE eu estou fazendo a requisição
        diretoria_regional = usuario.diretorias_regionais.first()
        inclusoes_normais = diretoria_regional.inclusoes_normais_reprovadas
        page = self.paginate_queryset(inclusoes_normais)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False,
            url_path='pedidos-prioritarios-codae/'
                     '(?P<filtro_aplicado>(sem_filtro|hoje|daqui_a_7_dias|daqui_a_30_dias)+)')
    def pedidos_prioritarios_codae(self, request, filtro_aplicado='sem_filtro'):
        usuario = request.user
        # TODO: aguardando definição de perfis pra saber em qual CODAE eu estou fazendo a requisição
        codae = usuario.CODAE.first()
        inclusoes_normais = codae.inclusoes_normais_das_minhas_escolas_no_prazo_vencendo(
            filtro_aplicado
        )
        page = self.paginate_queryset(inclusoes_normais)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False,
            url_path='pedidos-no-limite-codae/'
                     '(?P<filtro_aplicado>(sem_filtro|daqui_a_7_dias|daqui_a_30_dias)+)')
    def pedidos_no_limite_codae(self, request, filtro_aplicado='sem_filtro'):
        usuario = request.user
        # TODO: aguardando definição de perfis pra saber em qual CODAE eu estou fazendo a requisição
        codae = usuario.CODAE.first()
        inclusoes_normais = codae.inclusoes_normais_das_minhas_escolas_no_prazo_limite(
            filtro_aplicado
        )
        page = self.paginate_queryset(inclusoes_normais)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False,
            url_path='pedidos-no-prazo-codae/'
                     '(?P<filtro_aplicado>(sem_filtro|daqui_a_7_dias|daqui_a_30_dias)+)')
    def pedidos_no_prazo_codae(self, request, filtro_aplicado='sem_filtro'):
        usuario = request.user
        # TODO: aguardando definição de perfis pra saber em qual CODAE eu estou fazendo a requisição
        codae = usuario.CODAE.first()
        inclusoes_normais = codae.inclusoes_normais_das_minhas_escolas_no_prazo_regular(
            filtro_aplicado
        )
        page = self.paginate_queryset(inclusoes_normais)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path='pedidos-aprovados-codae')
    def pedidos_aprovados_codae(self, request):
        usuario = request.user
        # TODO: aguardando definição de perfis pra saber em qual CODAE eu estou fazendo a requisição
        codae = usuario.CODAE.first()
        inclusoes_normais = codae.inclusoes_normais_aprovadas
        page = self.paginate_queryset(inclusoes_normais)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path='pedidos-reprovados-codae')
    def pedidos_reprovados_codae(self, request):
        usuario = request.user
        # TODO: aguardando definição de perfis pra saber em qual CODAE eu estou fazendo a requisição
        codae = usuario.CODAE.first()
        inclusoes_normais = codae.inclusoes_normais_reprovadas
        page = self.paginate_queryset(inclusoes_normais)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False,
            url_path='pedidos-prioritarios-terceirizada/'
                     '(?P<filtro_aplicado>(sem_filtro|hoje|daqui_a_7_dias|daqui_a_30_dias)+)')
    def pedidos_prioritarios_terceirizada(self, request, filtro_aplicado='sem_filtro'):
        usuario = request.user
        # TODO: aguardando definição de perfis pra saber em qual Terceirizada eu estou fazendo a requisição
        terceirizada = usuario.terceirizadas.first()
        inclusoes_normais = terceirizada.inclusoes_normais_das_minhas_escolas_no_prazo_vencendo(
            filtro_aplicado
        )
        page = self.paginate_queryset(inclusoes_normais)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False,
            url_path='pedidos-no-limite-terceirizada/'
                     '(?P<filtro_aplicado>(sem_filtro|daqui_a_7_dias|daqui_a_30_dias)+)')
    def pedidos_no_limite_terceirizada(self, request, filtro_aplicado='sem_filtro'):
        usuario = request.user
        # TODO: aguardando definição de perfis pra saber em qual Terceirizada eu estou fazendo a requisição
        terceirizada = usuario.terceirizadas.first()
        inclusoes_normais = terceirizada.inclusoes_normais_das_minhas_escolas_no_prazo_limite(
            filtro_aplicado
        )
        page = self.paginate_queryset(inclusoes_normais)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False,
            url_path='pedidos-no-prazo-terceirizada/'
                     '(?P<filtro_aplicado>(sem_filtro|daqui_a_7_dias|daqui_a_30_dias)+)')
    def pedidos_no_prazo_terceirizada(self, request, filtro_aplicado='sem_filtro'):
        usuario = request.user
        # TODO: aguardando definição de perfis pra saber em qual Terceirizada eu estou fazendo a requisição
        terceirizada = usuario.terceirizadas.first()
        inclusoes_normais = terceirizada.inclusoes_normais_das_minhas_escolas_no_prazo_regular(
            filtro_aplicado
        )
        page = self.paginate_queryset(inclusoes_normais)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path='pedidos-aprovados-terceirizada')
    def pedidos_aprovados_terceirizada(self, request):
        usuario = request.user
        # TODO: aguardando definição de perfis pra saber em qual Terceirizada eu estou fazendo a requisição
        terceirizada = usuario.terceirizadas.first()
        inclusoes_normais = terceirizada.inclusoes_normais_aprovadas
        page = self.paginate_queryset(inclusoes_normais)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path='pedidos-reprovados-terceirizada')
    def pedidos_reprovados_terceirizada(self, request):
        usuario = request.user
        # TODO: aguardando definição de perfis pra saber em qual Terceirizada eu estou fazendo a requisição
        terceirizada = usuario.terceirizadas.first()
        inclusoes_normais = terceirizada.inclusoes_normais_reprovadas
        page = self.paginate_queryset(inclusoes_normais)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    #
    # IMPLEMENTACAO DO FLUXO
    #

    @action(detail=True, permission_classes=[PodeIniciarInclusaoAlimentacaoContinuaPermission],
            methods=['patch'], url_path=constants.ESCOLA_INICIO_PEDIDO)
    def inicio_de_pedido(self, request, uuid=None):
        grupo_alimentacao_normal = self.get_object()
        try:
            grupo_alimentacao_normal.inicia_fluxo(user=request.user, notificar=True)
            serializer = self.get_serializer(grupo_alimentacao_normal)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'))

    @action(detail=True, permission_classes=[PodeAprovarAlimentacaoContinuaDaEscolaPermission],
            methods=['patch'], url_path=constants.DRE_VALIDA_PEDIDO)
    def diretoria_regional_aprova(self, request, uuid=None):
        grupo_alimentacao_normal = self.get_object()
        try:
            grupo_alimentacao_normal.dre_valida(user=request.user, notificar=True)
            serializer = self.get_serializer(grupo_alimentacao_normal)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'))

    @action(detail=True, permission_classes=[PodeAprovarAlimentacaoContinuaDaEscolaPermission],
            methods=['patch'], url_path=constants.DRE_PEDE_REVISAO)
    def diretoria_regional_pede_revisao(self, request, uuid=None):
        grupo_alimentacao_normal = self.get_object()
        try:
            grupo_alimentacao_normal.dre_pede_revisao(user=request.user, notificar=True)
            serializer = self.get_serializer(grupo_alimentacao_normal)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'))

    @action(detail=True, permission_classes=[PodeAprovarAlimentacaoContinuaDaEscolaPermission],
            methods=['patch'], url_path=constants.DRE_NAO_VALIDA_PEDIDO)
    def diretoria_cancela_pedido(self, request, uuid=None):
        grupo_alimentacao_normal = self.get_object()
        try:
            grupo_alimentacao_normal.dre_nao_valida(user=request.user, notificar=True)
            serializer = self.get_serializer(grupo_alimentacao_normal)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'))

    @action(detail=True, permission_classes=[PodeAprovarAlimentacaoContinuaDaEscolaPermission],
            methods=['patch'], url_path=constants.ESCOLA_REVISA_PEDIDO)
    def escola_revisa_pedido(self, request, uuid=None):
        grupo_alimentacao_normal = self.get_object()
        try:
            grupo_alimentacao_normal.escola_revisa(user=request.user, notificar=True)
            serializer = self.get_serializer(grupo_alimentacao_normal)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'))

    @action(detail=True, permission_classes=[PodeAprovarAlimentacaoContinuaDaEscolaPermission],
            methods=['patch'], url_path=constants.CODAE_AUTORIZA_PEDIDO)
    def codae_aprova_pedido(self, request, uuid=None):
        grupo_alimentacao_normal = self.get_object()
        try:
            grupo_alimentacao_normal.codae_autoriza(user=request.user, notificar=True)
            serializer = self.get_serializer(grupo_alimentacao_normal)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'))

    @action(detail=True, permission_classes=[PodeAprovarAlimentacaoContinuaDaEscolaPermission],
            methods=['patch'], url_path=constants.CODAE_NEGA_PEDIDO)
    def codae_cancela_pedido(self, request, uuid=None):
        grupo_alimentacao_normal = self.get_object()
        try:
            grupo_alimentacao_normal.codae_nega(user=request.user, notificar=True)
            serializer = self.get_serializer(grupo_alimentacao_normal)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'))

    @action(detail=True, permission_classes=[PodeAprovarAlimentacaoContinuaDaEscolaPermission],
            methods=['patch'], url_path=constants.TERCEIRIZADA_TOMA_CIENCIA)
    def terceirizada_toma_ciencia(self, request, uuid=None):
        grupo_alimentacao_normal = self.get_object()
        try:
            grupo_alimentacao_normal.terceirizada_toma_ciencia(user=request.user, notificar=True)
            serializer = self.get_serializer(grupo_alimentacao_normal)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'))

    @action(detail=True, permission_classes=[PodeAprovarAlimentacaoContinuaDaEscolaPermission],
            methods=['patch'], url_path=constants.ESCOLA_CANCELA)
    def escola_cancela_pedido_48h_antes(self, request, uuid=None):
        grupo_alimentacao_normal = self.get_object()
        try:
            grupo_alimentacao_normal.cancelar_pedido(user=request.user, notificar=True)
            serializer = self.get_serializer(grupo_alimentacao_normal)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'))


class InclusaoAlimentacaoContinuaViewSet(ModelViewSet):
    lookup_field = 'uuid'
    queryset = InclusaoAlimentacaoContinua.objects.all()
    serializer_class = serializers.InclusaoAlimentacaoContinuaSerializer

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return serializers_create.InclusaoAlimentacaoContinuaCreationSerializer
        return serializers.InclusaoAlimentacaoContinuaSerializer

    @action(detail=False, url_path=constants.SOLICITACOES_DO_USUARIO)
    def minhas_solicitacoes(self, request):
        usuario = request.user
        inclusoes_continuas = InclusaoAlimentacaoContinua.get_solicitacoes_rascunho(usuario)
        page = self.paginate_queryset(inclusoes_continuas)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False,
            url_path=f'{constants.PEDIDOS_CODAE}/{constants.FILTRO_PADRAO_PEDIDOS}')
    def pedidos_codae(self, request, filtro_aplicado='sem_filtro'):
        # TODO: colocar regras de codae CODAE aqui...
        usuario = request.user
        # TODO: aguardando definição de perfis pra saber
        codae = usuario.CODAE.first()
        inclusoes_continuas = codae.inclusoes_alimentacao_continua_das_minhas_escolas(
            filtro_aplicado
        )
        page = self.paginate_queryset(inclusoes_continuas)
        serializer = serializers.InclusaoAlimentacaoContinuaSimplesSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False,
            url_path='pedidos-prioritarios-diretoria-regional/'
                     '(?P<filtro_aplicado>(sem_filtro|hoje|daqui_a_7_dias|daqui_a_30_dias)+)')
    def pedidos_prioritarios_diretoria_regional(self, request, filtro_aplicado='sem_filtro'):
        usuario = request.user
        # TODO: aguardando definição de perfis pra saber em qual DRE eu estou fazendo a requisição
        diretoria_regional = usuario.diretorias_regionais.first()
        inclusoes_continuas = diretoria_regional.inclusoes_continuas_das_minhas_escolas_no_prazo_vencendo(
            filtro_aplicado
        )
        page = self.paginate_queryset(inclusoes_continuas)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False,
            url_path='pedidos-no-limite-diretoria-regional/'
                     '(?P<filtro_aplicado>(sem_filtro|daqui_a_7_dias|daqui_a_30_dias)+)')
    def pedidos_no_limite_diretoria_regional(self, request, filtro_aplicado='sem_filtro'):
        usuario = request.user
        # TODO: aguardando definição de perfis pra saber em qual DRE eu estou fazendo a requisição
        diretoria_regional = usuario.diretorias_regionais.first()
        inclusoes_continuas = diretoria_regional.inclusoes_continuas_das_minhas_escolas_no_prazo_limite(
            filtro_aplicado
        )
        page = self.paginate_queryset(inclusoes_continuas)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False,
            url_path='pedidos-no-prazo-diretoria-regional/'
                     '(?P<filtro_aplicado>(sem_filtro|daqui_a_7_dias|daqui_a_30_dias)+)')
    def pedidos_no_prazo_diretoria_regional(self, request, filtro_aplicado='sem_filtro'):
        usuario = request.user
        # TODO: aguardando definição de perfis pra saber em qual DRE eu estou fazendo a requisição
        diretoria_regional = usuario.diretorias_regionais.first()
        inclusoes_continuas = diretoria_regional.inclusoes_continuas_das_minhas_escolas_no_prazo_regular(
            filtro_aplicado
        )
        page = self.paginate_queryset(inclusoes_continuas)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path='pedidos-aprovados-diretoria-regional')
    def pedidos_aprovados_diretoria_regional(self, request):
        usuario = request.user
        # TODO: aguardando definição de perfis pra saber em qual DRE eu estou fazendo a requisição
        diretoria_regional = usuario.diretorias_regionais.first()
        inclusoes_continuas = diretoria_regional.inclusoes_continuas_aprovadas
        page = self.paginate_queryset(inclusoes_continuas)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path='pedidos-reprovados-diretoria-regional')
    def pedidos_reprovados_diretoria_regional(self, request):
        usuario = request.user
        # TODO: aguardando definição de perfis pra saber em qual DRE eu estou fazendo a requisição
        diretoria_regional = usuario.diretorias_regionais.first()
        inclusoes_continuas = diretoria_regional.inclusoes_continuas_reprovadas
        page = self.paginate_queryset(inclusoes_continuas)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False,
            url_path='pedidos-prioritarios-codae/'
                     '(?P<filtro_aplicado>(sem_filtro|hoje|daqui_a_7_dias|daqui_a_30_dias)+)')
    def pedidos_prioritarios_codae(self, request, filtro_aplicado='sem_filtro'):
        usuario = request.user
        # TODO: aguardando definição de perfis pra saber em qual CODAE eu estou fazendo a requisição
        codae = usuario.CODAE.first()
        inclusoes_continuas = codae.inclusoes_continuas_das_minhas_escolas_no_prazo_vencendo(
            filtro_aplicado
        )
        page = self.paginate_queryset(inclusoes_continuas)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False,
            url_path='pedidos-no-limite-codae/'
                     '(?P<filtro_aplicado>(sem_filtro|daqui_a_7_dias|daqui_a_30_dias)+)')
    def pedidos_no_limite_codae(self, request, filtro_aplicado='sem_filtro'):
        usuario = request.user
        # TODO: aguardando definição de perfis pra saber em qual CODAE eu estou fazendo a requisição
        codae = usuario.CODAE.first()
        inclusoes_continuas = codae.inclusoes_continuas_das_minhas_escolas_no_prazo_limite(
            filtro_aplicado
        )
        page = self.paginate_queryset(inclusoes_continuas)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False,
            url_path='pedidos-no-prazo-codae/'
                     '(?P<filtro_aplicado>(sem_filtro|daqui_a_7_dias|daqui_a_30_dias)+)')
    def pedidos_no_prazo_codae(self, request, filtro_aplicado='sem_filtro'):
        usuario = request.user
        # TODO: aguardando definição de perfis pra saber em qual CODAE eu estou fazendo a requisição
        codae = usuario.CODAE.first()
        inclusoes_continuas = codae.inclusoes_continuas_das_minhas_escolas_no_prazo_regular(
            filtro_aplicado
        )
        page = self.paginate_queryset(inclusoes_continuas)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path='pedidos-aprovados-codae')
    def pedidos_aprovados_codae(self, request):
        usuario = request.user
        # TODO: aguardando definição de perfis pra saber em qual CODAE eu estou fazendo a requisição
        codae = usuario.CODAE.first()
        inclusoes_continuas = codae.inclusoes_continuas_aprovadas
        page = self.paginate_queryset(inclusoes_continuas)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path='pedidos-reprovados-codae')
    def pedidos_reprovados_codae(self, request):
        usuario = request.user
        # TODO: aguardando definição de perfis pra saber em qual CODAE eu estou fazendo a requisição
        codae = usuario.CODAE.first()
        inclusoes_continuas = codae.inclusoes_continuas_reprovadas
        page = self.paginate_queryset(inclusoes_continuas)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False,
            url_path='pedidos-prioritarios-terceirizada/'
                     '(?P<filtro_aplicado>(sem_filtro|hoje|daqui_a_7_dias|daqui_a_30_dias)+)')
    def pedidos_prioritarios_terceirizada(self, request, filtro_aplicado='sem_filtro'):
        usuario = request.user
        # TODO: aguardando definição de perfis pra saber em qual Terceirizada eu estou fazendo a requisição
        terceirizada = usuario.terceirizadas.first()
        inclusoes_continuas = terceirizada.inclusoes_continuas_das_minhas_escolas_no_prazo_vencendo(
            filtro_aplicado
        )
        page = self.paginate_queryset(inclusoes_continuas)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False,
            url_path='pedidos-no-limite-terceirizada/'
                     '(?P<filtro_aplicado>(sem_filtro|daqui_a_7_dias|daqui_a_30_dias)+)')
    def pedidos_no_limite_terceirizada(self, request, filtro_aplicado='sem_filtro'):
        usuario = request.user
        # TODO: aguardando definição de perfis pra saber em qual Terceirizada eu estou fazendo a requisição
        terceirizada = usuario.terceirizadas.first()
        inclusoes_continuas = terceirizada.inclusoes_continuas_das_minhas_escolas_no_prazo_limite(
            filtro_aplicado
        )
        page = self.paginate_queryset(inclusoes_continuas)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False,
            url_path='pedidos-no-prazo-terceirizada/'
                     '(?P<filtro_aplicado>(sem_filtro|daqui_a_7_dias|daqui_a_30_dias)+)')
    def pedidos_no_prazo_terceirizada(self, request, filtro_aplicado='sem_filtro'):
        usuario = request.user
        # TODO: aguardando definição de perfis pra saber em qual Terceirizada eu estou fazendo a requisição
        terceirizada = usuario.terceirizadas.first()
        inclusoes_continuas = terceirizada.inclusoes_continuas_das_minhas_escolas_no_prazo_regular(
            filtro_aplicado
        )
        page = self.paginate_queryset(inclusoes_continuas)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path='pedidos-aprovados-terceirizada')
    def pedidos_aprovados_terceirizada(self, request):
        usuario = request.user
        # TODO: aguardando definição de perfis pra saber em qual Terceirizada eu estou fazendo a requisição
        terceirizada = usuario.terceirizadas.first()
        inclusoes_continuas = terceirizada.inclusoes_continuas_aprovadas
        page = self.paginate_queryset(inclusoes_continuas)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path='pedidos-reprovados-terceirizada')
    def pedidos_reprovados_terceirizada(self, request):
        usuario = request.user
        # TODO: aguardando definição de perfis pra saber em qual Terceirizada eu estou fazendo a requisição
        terceirizada = usuario.terceirizadas.first()
        inclusoes_continuas = terceirizada.inclusoes_continuas_reprovadas
        page = self.paginate_queryset(inclusoes_continuas)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    #
    # IMPLEMENTACAO DO FLUXO
    #

    @action(detail=True, permission_classes=[PodeIniciarInclusaoAlimentacaoContinuaPermission],
            methods=['patch'], url_path=constants.ESCOLA_INICIO_PEDIDO)
    def inicio_de_pedido(self, request, uuid=None):
        inclusao_alimentacao_continua = self.get_object()
        try:
            inclusao_alimentacao_continua.inicia_fluxo(user=request.user, notificar=True)
            serializer = self.get_serializer(inclusao_alimentacao_continua)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'))

    @action(detail=True, permission_classes=[PodeAprovarAlimentacaoContinuaDaEscolaPermission],
            methods=['patch'], url_path=constants.DRE_VALIDA_PEDIDO)
    def diretoria_regional_aprova(self, request, uuid=None):
        inclusao_alimentacao_continua = self.get_object()
        try:
            inclusao_alimentacao_continua.dre_valida(user=request.user, notificar=True)
            serializer = self.get_serializer(inclusao_alimentacao_continua)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'))

    @action(detail=True, permission_classes=[PodeAprovarAlimentacaoContinuaDaEscolaPermission],
            methods=['patch'], url_path=constants.DRE_PEDE_REVISAO)
    def diretoria_regional_pede_revisao(self, request, uuid=None):
        inclusao_alimentacao_continua = self.get_object()
        try:
            inclusao_alimentacao_continua.dre_pede_revisao(user=request.user, notificar=True)
            serializer = self.get_serializer(inclusao_alimentacao_continua)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'))

    @action(detail=True, permission_classes=[PodeAprovarAlimentacaoContinuaDaEscolaPermission],
            methods=['patch'], url_path=constants.ESCOLA_REVISA_PEDIDO)
    def escola_revisa_pedido(self, request, uuid=None):
        inclusao_alimentacao_continua = self.get_object()
        try:
            inclusao_alimentacao_continua.escola_revisa(user=request.user, notificar=True)
            serializer = self.get_serializer(inclusao_alimentacao_continua)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'))

    @action(detail=True, permission_classes=[PodeAprovarAlimentacaoContinuaDaEscolaPermission],
            methods=['patch'], url_path=constants.CODAE_NEGA_PEDIDO)
    def codae_cancela_pedido(self, request, uuid=None):
        inclusao_alimentacao_continua = self.get_object()
        try:
            inclusao_alimentacao_continua.codae_nega(user=request.user, notificar=True)
            serializer = self.get_serializer(inclusao_alimentacao_continua)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'))

    @action(detail=True, permission_classes=[PodeAprovarAlimentacaoContinuaDaEscolaPermission],
            methods=['patch'], url_path=constants.DRE_NAO_VALIDA_PEDIDO)
    def diretoria_regional_cancela_pedido(self, request, uuid=None):
        inclusao_alimentacao_continua = self.get_object()
        try:
            inclusao_alimentacao_continua.dre_nao_valida(user=request.user, notificar=True)
            serializer = self.get_serializer(inclusao_alimentacao_continua)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'))

    @action(detail=True, permission_classes=[PodeAprovarAlimentacaoContinuaDaEscolaPermission],
            methods=['patch'], url_path=constants.CODAE_AUTORIZA_PEDIDO)
    def codae_aprova_pedido(self, request, uuid=None):
        inclusao_alimentacao_continua = self.get_object()
        try:
            inclusao_alimentacao_continua.codae_autoriza(user=request.user, notificar=True)
            serializer = self.get_serializer(inclusao_alimentacao_continua)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'))

    @action(detail=True, permission_classes=[PodeAprovarAlimentacaoContinuaDaEscolaPermission],
            methods=['patch'], url_path=constants.TERCEIRIZADA_TOMA_CIENCIA)
    def terceirizada_toma_ciencia(self, request, uuid=None):
        inclusao_alimentacao_continua = self.get_object()
        try:
            inclusao_alimentacao_continua.terceirizada_toma_ciencia(user=request.user, notificar=True)
            serializer = self.get_serializer(inclusao_alimentacao_continua)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'))

    @action(detail=True, permission_classes=[PodeAprovarAlimentacaoContinuaDaEscolaPermission],
            methods=['patch'], url_path=constants.ESCOLA_CANCELA)
    def escola_cancela_pedido_48h_antes(self, request, uuid=None):
        inclusao_alimentacao_continua = self.get_object()
        try:
            inclusao_alimentacao_continua.cancelar_pedido(user=request.user, notificar=True)
            serializer = self.get_serializer(inclusao_alimentacao_continua)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'))

    def destroy(self, request, *args, **kwargs):
        inclusao_alimentacao_continua = self.get_object()
        if inclusao_alimentacao_continua.pode_excluir:
            return super().destroy(request, *args, **kwargs)
