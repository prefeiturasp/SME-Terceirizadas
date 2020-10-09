from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from ..utils import EOLException, EOLService


class DadosUsuarioEOLViewSet(ViewSet):
    lookup_field = 'registro_funcional'
    permission_classes = (IsAuthenticated,)

    def retrieve(self, request, registro_funcional=None):
        try:
            dados = EOLService.get_informacoes_usuario(registro_funcional)
            for dado in dados:
                dado.pop('cd_cpf_pessoa')  # retira cpf por ser dado sensivel
            return Response({'detail': dados})
        except EOLException as e:
            return Response({'detail': f'{e}'}, status=status.HTTP_400_BAD_REQUEST)


class DadosAlunoEOLViewSet(ViewSet):
    lookup_field = 'codigo_eol'
    permission_classes = (IsAuthenticated,)

    def retrieve(self, request, codigo_eol=None):
        try:
            dados = EOLService.get_informacoes_aluno(codigo_eol)
            return Response({'detail': dados})
        except EOLException as e:
            return Response({'detail': f'{e}'}, status=status.HTTP_400_BAD_REQUEST)
