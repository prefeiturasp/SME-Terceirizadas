from django.db import models

from ...dados_comuns.behaviors import (
    Ativavel, Descritivel, IntervaloDeDia, Nomeavel, TemChaveExterna
)


class Vinculo(IntervaloDeDia, Ativavel, TemChaveExterna):
    """Para informar que tipo de funcao uma pessoa teve em um dado intervalo de tempo em uma instituição.

    Ex.: de jan a dez de 2018 (Intervalo) Ciclano (Usuário) foi Diretor (Perfil)
    """

    perfil = models.ForeignKey('Perfil', on_delete=models.PROTECT)
    usuario = models.ForeignKey('Usuario', on_delete=models.PROTECT)

    class Meta:
        verbose_name = 'Vínculo'
        verbose_name_plural = 'Vínculos'

    def __str__(self):
        return ''


class Perfil(Nomeavel, Descritivel, Ativavel, TemChaveExterna):
    """Perfil do usuário Ex: Cogestor, Nutricionista. Cada perfil tem uma série de permissoes."""

    super_usuario = models.BooleanField('Super usuario na instiuição?', default=False)

    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfis'

    def __str__(self):
        return self.nome
