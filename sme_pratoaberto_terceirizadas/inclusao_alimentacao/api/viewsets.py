from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet

from sme_pratoaberto_terceirizadas.inclusao_alimentacao.api.serializers import MotivoInclusaoContinuaSerializer, \
    InclusaoAlimentacaoNormalSerializer, GrupoInclusaoAlimentacaoNormalSerializer
from sme_pratoaberto_terceirizadas.inclusao_alimentacao.models import MotivoInclusaoContinua, InclusaoAlimentacaoNormal, \
    GrupoInclusaoAlimentacaoNormal


# class InclusaoAlimentacaoViewSet(ModelViewSet):
#     """
#     Endpoint para Inclusão de Alimentação
#     """
#     queryset = InclusaoAlimentacao.objects.all()
#     serializer_class = InclusaoAlimentacaoSerializer
#     object_class = InclusaoAlimentacao
#
#     @action(detail=False, methods=['get'])
#     def obter_motivos(self, request):
#         response = {'content': {}, 'log_content': {}, 'code': None}
#         try:
#             motivo_simples = MotivoInclusaoAlimentacao.objects.exclude(nome__icontains='Programa Contínuo').filter(
#                 ativo=True)
#             motivo_programa_continuo = MotivoInclusaoAlimentacao.objects.filter(nome__icontains='Programa Contínuo',
#                                                                             ativo=True)
#         except Http404:
#             response['log_content'] = ["Usuário não encontrado"]
#             response['code'] = status.HTTP_404_NOT_FOUND
#         else:
#             response['code'] = status.HTTP_200_OK
#             response['content']['motivo_simples'] = MotivoInclusaoAlimentacaoSerializer(motivo_simples, many=True).data
#             response['content']['motivo_programa_continuo'] = MotivoInclusaoAlimentacaoSerializer(
#                 motivo_programa_continuo, many=True).data
#         return Response(response, status=response['code'])
#
#     @action(detail=False, methods=['get'])
#     def obter_inclusao_alimentacao_salva(self, request):
#         response = {'content': {}, 'log_content': {}, 'code': None}
#         try:
#             user = request.user
#             inclusao_alimentacao = InclusaoAlimentacao.objects.filter(status__nome=InclusaoAlimentacaoStatus.SALVO, criado_por=user)
#         except Http404:
#             response['log_content'] = ["Usuário não encontrado"]
#             response['code'] = status.HTTP_404_NOT_FOUND
#         else:
#             response['code'] = status.HTTP_200_OK
#             response['content']['inclusao_alimentacao'] = InclusaoAlimentacaoSerializer(inclusao_alimentacao, many=True).data
#         return Response(response, status=response['code'])
#
#     @action(detail=False, methods=['post'])
#     def criar_ou_atualizar(self, request):
#         response = {'content': {}, 'log_content': {}, 'code': None}
#         lista_erros = list()
#         try:
#             user = request.user
#             lista_erros = obter_lista_erros(request.data)
#             if lista_erros:
#                 raise InclusaoAlimentacaoCriarOuAtualizarException(_('alguns argumentos não são válidos'))
#             uuid = request.data.get('uuid', None)
#             inclusao_alimentacao = get_object_or_404(InclusaoAlimentacao, uuid=uuid) if uuid else InclusaoAlimentacao()
#             if uuid:
#                 assert inclusao_alimentacao.status in [InclusaoAlimentacaoStatus.objects.get(name=InclusaoAlimentacaoStatus.A_EDITAR),
#                                                  InclusaoAlimentacaoStatus.objects.get(name=InclusaoAlimentacaoStatus.SALVO)], \
#                     "Inclusão de Alimentação não está com status válido para edição"
#                 inclusao_alimentacao.motivos.all().delete()
#                 inclusao_alimentacao.motivos.all().delete()
#             inclusao_alimentacao.criar_ou_alterar(request_data=request.data, user=user)
#             validacao_diff = 'creation' if not uuid else 'edition'
#             if inclusao_alimentacao.status.nome != InclusaoAlimentacaoStatus.SALVO:
#                 inclusao_alimentacao.enviar_notificacao(user, validacao_diff)
#         except Http404 as error:
#             response['log_content'] = [_('usuario nao encontrado')] if 'User' in str(error) else [_('inclusao alimentacao nao encontrada')]
#             response['code'] = status.HTTP_404_NOT_FOUND
#         except AssertionError as error:
#             response['log_content'] = [str(error)]
#             response['code'] = status.HTTP_400_BAD_REQUEST
#         except InclusaoAlimentacaoCriarOuAtualizarException:
#             response['log_content'] = lista_erros
#             response['code'] = status.HTTP_400_BAD_REQUEST
#         else:
#             response['code'] = status.HTTP_200_OK
#             response['content']['food_inclusion'] = InclusaoAlimentacaoSerializer(inclusao_alimentacao).data
#         return Response(response, status=response['code'])
#
#     @action(detail=False, methods=['delete'])
#     def delete(self, request):
#         response = {'content': {}, 'log_content': {}, 'code': None}
#         try:
#             user = request.user
#             uuid = request.data.get('uuid', None)
#             inclusao_alimentacao = get_object_or_404(InclusaoAlimentacao, uuid=uuid, created_by=user)
#             assert inclusao_alimentacao.status == InclusaoAlimentacaoStatus.objects.get(nome=InclusaoAlimentacaoStatus.SALVO), \
#                 "Status de inclusão não está como SALVO"
#             inclusao_alimentacao.delete()
#         except Http404 as error:
#             response['log_content'] = ['Usuário não encontrado'] if 'User' in str(error) else [
#                 'Inclusão de alimentação não encontrada']
#             response['code'] = status.HTTP_404_NOT_FOUND
#         except AssertionError as error:
#             response['code'] = status.HTTP_400_BAD_REQUEST
#             response['log_content'] = [str(error)]
#         else:
#             response['code'] = status.HTTP_200_OK
#         return Response(response, status=response['code'])
#
#     @action(detail=False, methods=['post'])
#     def validate(self, request):
#         response = {'content': {}, 'log_content': {}, 'code': None}
#         try:
#             user = request.user
#             assert checar_dados_genericos_requeridos(request.data, ['uuid', 'resposta_validacao']), \
#                 _('missing arguments')
#             resposta_validacao = request.data.get('resposta_validacao')
#             uuid = request.data.get('uuid')
#             inclusao_alimentacao = get_object_or_404(InclusaoAlimentacao, uuid=uuid)
#             assert inclusao_alimentacao.status == InclusaoAlimentacaoStatus.objects.get(nome=InclusaoAlimentacaoStatus.A_VALIDAR), \
#                 _('status da inclusao de alimentacao nao e valido')
#             novo_status = InclusaoAlimentacaoStatus.objects.get(nome=InclusaoAlimentacaoStatus.A_APROVAR) if resposta_validacao \
#                 else InclusaoAlimentacaoStatus.objects.get(InclusaoAlimentacaoStatus.A_EDITAR)
#             inclusao_alimentacao.status = novo_status
#             inclusao_alimentacao.save()
#             inclusao_alimentacao.send_notification(user)
#         except Http404 as error:
#             response['log_content'] = [_('usuario nao encontrado')] if 'User' in str(error) else [_('inclusao de alimentacao nao encontrada')]
#             response['code'] = status.HTTP_404_NOT_FOUND
#         except AssertionError as assertionError:
#             response['log_content'] = str(assertionError)
#             response['code'] = status.HTTP_400_BAD_REQUEST
#         else:
#             response['code'] = status.HTTP_200_OK
#             response['content']['food_inclusion'] = InclusaoAlimentacaoSerializer(inclusao_alimentacao).data
#         return Response(response, status=response['code'])
#
#     @action(detail=False, methods=['post'])
#     def approve(self, request):
#         response = {'content': {}, 'log_content': {}, 'code': None}
#         try:
#             user = request.user
#             resposta_aprovacao = request.data.get('resposta_aprovacao')
#             uuid = request.data.get('uuid')
#             inclusao_alimentacao = get_object_or_404(InclusaoAlimentacao, uuid=uuid)
#             assert inclusao_alimentacao.status == InclusaoAlimentacaoStatus.objects.get(nome=InclusaoAlimentacaoStatus.A_APROVAR), \
#                 _('status inclusao de alimentacao nao aprovado')
#             novo_status = InclusaoAlimentacaoStatus.objects.get(nome=InclusaoAlimentacaoStatus.A_VISUALIZAR) if resposta_aprovacao \
#                 else InclusaoAlimentacaoStatus.objects.get(nome=InclusaoAlimentacaoStatus.NEGADO_PELA_CODAE)
#             inclusao_alimentacao.status = novo_status
#             inclusao_alimentacao.save()
#             inclusao_alimentacao.send_notification(user)
#         except Http404 as error:
#             response['log_content'] = [_('usuario nao encontrado')] if 'User' in str(error) else [_('inclusao de alimentacao nao encontrada')]
#             response['code'] = status.HTTP_404_NOT_FOUND
#         except InclusaoAlimentacaoCriarOuAtualizarException:
#             response['code'] = status.HTTP_400_BAD_REQUEST
#         else:
#             response['code'] = status.HTTP_200_OK
#             response['content']['inclusao_alimentacao'] = InclusaoAlimentacaoSerializer(inclusao_alimentacao).data
#         return Response(response, status=response['code'])
#
#     @action(detail=False, methods=['post'])
#     def visualize(self, request):
#         response = {'content': {}, 'log_content': {}, 'code': None}
#         try:
#             user = request.user
#             uuid = request.data.get('uuid')
#             inclusao_alimentacao = get_object_or_404(InclusaoAlimentacao, uuid=uuid)
#             assert inclusao_alimentacao.status == InclusaoAlimentacaoStatus.objects.get(nome=InclusaoAlimentacaoStatus.A_VISUALIZAR), \
#                 _('status inclusao de alimentacao é nao visualizado')
#             aceito_pela_terceirizada = request.data.get('aceito_pela_terceirizada', True)
#             if aceito_pela_terceirizada:
#                 novo_status = InclusaoAlimentacaoStatus.objects.get(nome=InclusaoAlimentacaoStatus.VISUALIZADO)
#             else:
#                 novo_status = InclusaoAlimentacaoStatus.objects.get(nome=InclusaoAlimentacaoStatus.NEGADO_PELA_CODAE)
#                 inclusao_alimentacao.motivo_recusa = request.data.get('motivo_recusa')
#             inclusao_alimentacao.status = novo_status
#             inclusao_alimentacao.save()
#             inclusao_alimentacao.send_notification(user)
#         except Http404 as error:
#             response['log_content'] = [_('usuario nao encontrado')] if 'User' in str(error) else [_('inclusao de alimentacao nao encontrada')]
#             response['code'] = status.HTTP_404_NOT_FOUND
#         except InclusaoAlimentacaoCriarOuAtualizarException:
#             response['code'] = status.HTTP_400_BAD_REQUEST
#         else:
#             response['code'] = status.HTTP_200_OK
#             response['content']['inclusao_alimentacao'] = InclusaoAlimentacaoSerializer(inclusao_alimentacao).data
#         return Response(response, status=response['code'])

class MotivoInclusaoContinuaViewSet(ReadOnlyModelViewSet):
    lookup_field = 'uuid'
    queryset = MotivoInclusaoContinua.objects.all()
    serializer_class = MotivoInclusaoContinuaSerializer


class InclusaoAlimentacaoNormalViewSet(ModelViewSet):
    lookup_field = 'uuid'
    queryset = InclusaoAlimentacaoNormal.objects.all()
    serializer_class = InclusaoAlimentacaoNormalSerializer


class GrupoInclusaoAlimentacaoNormalViewSet(ModelViewSet):
    lookup_field = 'uuid'
    queryset = GrupoInclusaoAlimentacaoNormal.objects.all()
    serializer_class = GrupoInclusaoAlimentacaoNormalSerializer
