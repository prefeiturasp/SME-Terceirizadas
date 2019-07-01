from rest_framework import status
from rest_framework.response import Response

from sme_pratoaberto_terceirizadas.alimentacao.api.utils import valida_usuario_vinculado_escola, notifica_dres
from sme_pratoaberto_terceirizadas.alimentacao.models import InverterDiaCardapio
from sme_pratoaberto_terceirizadas.users.models import User


def valida_ja_existe(data):
    if InverterDiaCardapio.ja_existe(data):
        return False
    return True


def valida_dia_hoje(data):
    return InverterDiaCardapio.valida_dia_atual(data)


def valida_dia_util(data):
    return InverterDiaCardapio.valida_fim_semana(data)


def valida_feriado(data):
    return InverterDiaCardapio.valida_feriado(data)


def valida_vinculo_escola(usuario: User):
    if valida_usuario_vinculado_escola(usuario):
        return True
    return False


def validacao_e_solicitacao(request):
    if not valida_ja_existe(request.data):
        return Response({'error': 'Já existe uma solicitação registrada com estes dados informados'},
                        status=status.HTTP_409_CONFLICT)
    if not valida_usuario_vinculado_escola(request.user):
        return Response({'error': 'Usuário sem relacionamento a uma escola'}, status=status.HTTP_409_CONFLICT)
    if not valida_dia_hoje(request.data):
        return Response({'error': 'Não é possivel solicitar dia de hoje para inversão'},
                        status=status.HTTP_409_CONFLICT)
    if not valida_feriado(request.data):
        return Response({'error': 'Não é possivel solicitar feriado para inversão'},
                        status=status.HTTP_409_CONFLICT)
    if not valida_dia_util(request.data):
        return Response({'error': 'Não é possivel solicitar fim de semana para alteração'},
                        status=status.HTTP_409_CONFLICT)

    obj = InverterDiaCardapio.solicitar(request.data, request.user)
    if obj:
        notifica_dres(obj.usuario, obj.escola, obj.data_de, obj.data_para)
        return Response({'success': 'Solicitação efetuada com sucesso.'}, status=status.HTTP_201_CREATED)
    else:
        return Response({'error': 'Ocorreu um erro ao tentar salvar solicitação, tente novamente'},
                        status=status.HTTP_502_BAD_GATEWAY)


def validacao_e_salvamento(request):
    if not valida_ja_existe(request.data):
        return Response({'error': 'Já existe uma solicitação registrada com estes dados informados'},
                        status=status.HTTP_409_CONFLICT)
    if not valida_usuario_vinculado_escola(request.user):
        return Response({'error': 'Usuário sem relacionamento a uma escola'}, status=status.HTTP_409_CONFLICT)
    if not valida_dia_hoje(request.data):
        return Response({'error': 'Não é possivel solicitar dia de hoje para inversão'},
                        status=status.HTTP_409_CONFLICT)
    if not valida_feriado(request.data):
        return Response({'error': 'Não é possivel solicitar feriado para inversão'},
                        status=status.HTTP_409_CONFLICT)
    if not valida_dia_util(request.data):
        return Response({'error': 'Não é possivel solicitar final de semana para inversão'},
                        status=status.HTTP_409_CONFLICT)

    obj = InverterDiaCardapio.salvar_solicitacao(request.data, request.user)
    if obj:
        return Response({'success': 'Solicitação salva com sucesso.'}, status=status.HTTP_201_CREATED)
    else:
        return Response({'error': 'Ocorreu um erro ao tentar salvar solicitação, tente novamente'},
                        status=status.HTTP_502_BAD_GATEWAY)
