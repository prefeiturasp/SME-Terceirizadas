import datetime

from rest_framework import viewsets, status
from rest_framework.response import Response

from sme_pratoaberto_terceirizadas.escola.models import DiretoriaRegional


class DrePendentesAprovacaoViewSet(viewsets.ViewSet):

    def list(self, request):
        usuario = request.user
        dre = DiretoriaRegional.objects.filter(usuarios=usuario).first()
        response = []
        for alteracao in dre.alteracoes_cardapio_das_minhas_escolas_pendentes.all():
            nova_alteracao = {
                'text': f'{alteracao.id_externo} - {alteracao.escola.lote} - Alteração de Cardápio',
                'date': f'{alteracao.data_inicial}'
            }

            response.append(nova_alteracao)

        return Response(response, status=status.HTTP_200_OK)

