from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from sme_terceirizadas.escola.models import Aluno

from ..utils import EOLException, EOLService, EOLServicoSGP


class DadosUsuarioEOLCompletoViewSet(ViewSet):
    lookup_field = 'registro_funcional'
    permission_classes = (IsAuthenticated,)

    def retrieve(self, request, registro_funcional=None):
        try:
            dados_ciedu = EOLService.get_informacoes_usuario(registro_funcional)
            dados_sme = EOLServicoSGP.usuario_core_sso_or_none(registro_funcional)
            dados_usuario = {}
            if dados_ciedu[0] and dados_sme:
                dados_usuario = {
                    'nome': dados_sme['nome'],
                    'email': dados_sme['email'],
                    'cpf': dados_sme['cpf'],
                    'rf': dados_sme['codigoRf'],
                    'cargo': dados_ciedu[0]['cargo'],
                    'codigo_eol_unidade': dados_ciedu[0]['cd_divisao'],
                }
            return Response(dados_usuario)
        except EOLException as e:
            return Response({'detail': f'{e}'}, status=status.HTTP_400_BAD_REQUEST)


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
        """informação importante.

        Antes a consulta era feita na API do eol porém agora temos uma task que
        roda todos os dia e importa os alunos.
        Só mantive a resposta igual a do eol por conveniência para não precisar
        mudar o front no momento dessa atulização

        resposta:
         {
            'cd_aluno': 0001234,
            'nm_aluno': 'XXXXXX',
            'nm_social_aluno': None,
            'dt_nascimento_aluno': '1973-08-14T00:00:00',
            'cd_sexo_aluno': 'M',
            'nm_mae_aluno': 'XXXXX',
            'nm_pai_aluno': 'XXXX',
            'cd_escola': '017981',
            'dc_turma_escola': '4C',
            'dc_tipo_turno': 'Manhã'
        }
        """
        try:
            aluno: Aluno = Aluno.objects.filter(codigo_eol=codigo_eol).get()
            dados = {
                'cd_aluno': aluno.codigo_eol,
                'nm_aluno': aluno.nome,
                'nm_social_aluno': None,
                'dt_nascimento_aluno': f'{aluno.data_nascimento.strftime("%Y-%m-%d")}T00:00:00',
                'cd_sexo_aluno': None,
                'nm_mae_aluno': None,
                'nm_pai_aluno': None,
                'cd_escola': aluno.escola.codigo_eol,
                'dc_turma_escola': aluno.serie,
                # TODO: investigar e tratar AttributeError para aluno.periodo_escolar.nome
                # ('NoneType' object has no attribute 'nome')
                # 'dc_tipo_turno': aluno.periodo_escolar.nome
            }
            return Response({'detail': dados})
        except EOLException as e:
            return Response({'detail': f'{e}'}, status=status.HTTP_400_BAD_REQUEST)
        except Aluno.DoesNotExist as error:
            # O front está esperando BAD_REQUEST
            return Response({'detail': f'{error}'}, status=status.HTTP_400_BAD_REQUEST)
