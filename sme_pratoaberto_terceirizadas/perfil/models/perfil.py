from django.db import models

from ...dados_comuns.models_abstract import (Nomeavel, Descritivel, Ativavel, TemChaveExterna)


class GrupoPerfil(Nomeavel, Descritivel, Ativavel, TemChaveExterna):
    """
        grupo CODAE: tem os perfis gerente1, sup2, etc.
        grupo ESCOLA: tem os perfis prof, diretor, etc.
    """

    class Meta:
        verbose_name = 'Grupo de perfil'
        verbose_name_plural = 'Grupos de perfis'

    def __str__(self):
        return self.nome


class Permissao(Nomeavel, Ativavel, TemChaveExterna):
    """
    Permissões do usuário:
    Ex. Pode fazer compra,
        pode abrir a escola,
        pode fazer merenda,
        pode dar aula,
        pode fechar a escola, etc.
    """

    class Meta:
        verbose_name = 'Permissão'
        verbose_name_plural = 'Permissões'

    def __str__(self):
        return self.nome


class Perfil(Nomeavel, Descritivel, Ativavel, TemChaveExterna):
    """
    Perfil do usuário Ex: Cogestor, Nutricionista. Cada perfil tem uma série de permissoes.

    Ex: o perfil diretor tem as permissões: [abrir escola, fechar escola]
        o perfil professor pode [dar aula]
    """
    permissoes = models.ManyToManyField(Permissao)
    grupo = models.ForeignKey(GrupoPerfil, on_delete=models.DO_NOTHING,
                              related_name='perfis',
                              null=True, blank=True)

    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfis'

    def __str__(self):
        return self.nome
