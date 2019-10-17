from django.contrib.postgres.fields import ArrayField
from django.db import models

from ...dados_comuns.models_abstract import (
    Ativavel, Descritivel, Nomeavel, TemChaveExterna
)


class GrupoPerfil(Nomeavel, Descritivel, Ativavel, TemChaveExterna):
    """Para agupar perfis.

    - grupo CODAE: tem os perfis gerente1, sup2, etc.
    - grupo ESCOLA: tem os perfis prof, diretor, etc.
    """

    class Meta:
        verbose_name = 'Grupo de perfil'
        verbose_name_plural = 'Grupos de perfis'

    def __str__(self):
        return self.nome


class Permissao(Nomeavel, Ativavel, TemChaveExterna):
    """Permissões do usuário.

    - pode fazer compra,
    - pode abrir a escola,
    - pode fazer merenda,
    - pode dar aula,
    - pode fechar a escola, etc.
    """

    class Meta:
        verbose_name = 'Permissão'
        verbose_name_plural = 'Permissões'

    def __str__(self):
        return self.nome


class Perfil(Nomeavel, Descritivel, Ativavel, TemChaveExterna):
    """Perfil do usuário Ex: Cogestor, Nutricionista. Cada perfil tem uma série de permissoes.

    Ex:
    - o perfil diretor tem as permissões: [abrir escola, fechar escola]
    - o perfil professor pode [dar aula]
    """

    grupo = models.ForeignKey(GrupoPerfil, on_delete=models.DO_NOTHING,
                              related_name='perfis',
                              null=True, blank=True)

    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfis'

    def __str__(self):
        return self.nome


class PerfilPermissao(models.Model):
    """Para uso em conjunto com Perfil.

    Permissões do usuário:
    Ex. Pode fazer compra,
    pode abrir a escola,
    pode fazer merenda,
    pode dar aula,
    pode fechar a escola, etc.
    """

    CRIA = 0
    VISUALIZA = 1
    CANCELA = 2
    EDITA = 3
    RECEBE = 4
    FICA_CIENTE = 5
    CIENTE_APOS_AUTORIZACAO = 6

    ACOES = (
        (CRIA, 'Cria'),
        (VISUALIZA, 'Visualiza'),
        (EDITA, 'Edita'),
        (CANCELA, 'Cancela'),
        (RECEBE, 'Recebe'),
        (FICA_CIENTE, 'Fica ciente'),
        (CIENTE_APOS_AUTORIZACAO, 'Ciente após autorização'),
    )

    acoes = ArrayField(models.PositiveSmallIntegerField(choices=ACOES,
                                                        default=[],
                                                        null=True, blank=True))
    permissao = models.ForeignKey(Permissao, on_delete=models.DO_NOTHING)
    perfil = models.ForeignKey(Perfil, on_delete=models.DO_NOTHING)

    def acoes_choices_array_display(self):
        result = ''
        choices = dict(self.ACOES)
        for index, value in enumerate(self.acoes):
            result += '{0}'.format(choices[value])
            if not index == len(self.acoes) - 1:
                result += ', '
        return result

    def __str__(self):
        return f'{self.perfil} Tem ações: ({self.acoes_choices_array_display()}) da permissão {self.permissao}'
