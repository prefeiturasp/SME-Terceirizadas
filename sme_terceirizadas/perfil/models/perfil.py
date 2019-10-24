from django.db import models

from ...dados_comuns.behaviors import (
    Ativavel, Descritivel, Nomeavel, TemChaveExterna
)


class Vinculo(Ativavel, TemChaveExterna):
    """Para informar que tipo de funcao uma pessoa teve em um dado intervalo de tempo em uma instituição.

    Ex.: de jan a dez de 2018 (Intervalo) Ciclano (Usuário) foi Diretor (Perfil)
    """

    data_inicial = models.DateField('Data inicial')
    data_final = models.DateField('Data final', null=True, blank=True)
    perfil = models.ForeignKey('Perfil', on_delete=models.PROTECT)
    usuario = models.ForeignKey('Usuario', on_delete=models.PROTECT, related_name='vinculos')

    class Meta:
        verbose_name = 'Vínculo'
        verbose_name_plural = 'Vínculos'

    def __str__(self):
        return f'{self.usuario} de {self.data_inicial} até {self.data_final}'


class Perfil(Nomeavel, Descritivel, Ativavel, TemChaveExterna):
    """Perfil do usuário Ex: Cogestor, Nutricionista. Cada perfil tem uma série de permissoes."""

    super_usuario = models.BooleanField('Super usuario na instiuição?', default=False)

    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfis'

    def __str__(self):
        return self.nome
