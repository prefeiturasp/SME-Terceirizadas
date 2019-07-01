from django.db import models

from ...dados_comuns.models_abstract import Nomeavel, Descritivel, Ativavel


class GrupoPerfil(Nomeavel, Descritivel, Ativavel):
    """
        grupo CODAE: tem os perfis gerente1, sup2, etc.
        grupo ESCOLA: tem os perfis prof, diretor, etc.
    """


class Permissao(Nomeavel, Ativavel):
    """
    Permissões do usuário:
    Ex. Pode fazer compra,
        pode abrir a escola,
        pode fazer merenda,
        pode dar aula,
        pode fechar a escola, etc.
    """


class Perfil(Nomeavel, Descritivel, Ativavel):
    """
    Perfil do usuário Ex: Cogestor, Nutricionista. Cada perfil tem uma série de permissoes.

    Ex: o perfil diretor tem as permissões: [abrir escola, fechar escola]
        o perfil professor pode [dar aula]
    """
    permissoes = models.ManyToManyField(Permissao)
    grupo = models.ForeignKey(GrupoPerfil, on_delete=models.DO_NOTHING, null=True, blank=True)
