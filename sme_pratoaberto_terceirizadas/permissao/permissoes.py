from rest_framework import permissions
from .models import Permissao, PerfilPermissao
from django.core.exceptions import ObjectDoesNotExist


class ValidarPermissao(permissions.BasePermission):

    def has_permission(self, request, view):
        if (self._validar_perfil_e_permissao(request)):
            return True

        return False

    def _validar_perfil_e_permissao(self, request):
        try:
            endpoint = request.get_full_path()

            perfil = request.user.profile

            permissao = Permissao.objects.get(endpoint=endpoint)

            permissao_concedida = PerfilPermissao.objects.filter(perfil=perfil, permissao=permissao)

            permissao_acao = self._valida_request_leitura_ou_escrita(request.method, permissao_concedida.get().verbs)

            if permissao_concedida:
                return permissao_acao

            return False

        except ObjectDoesNotExist:
            return False

    def _valida_request_leitura_ou_escrita(self, method, acao):
        if method in permissions.SAFE_METHODS and acao == 'R':
            return True
        elif acao == 'W':
            return True

        return False
