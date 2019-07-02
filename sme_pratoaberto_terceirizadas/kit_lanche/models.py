from django.db import models

from sme_pratoaberto_terceirizadas.dados_comuns.models_abstract import Nomeavel, TemData, Motivo, Descritivel, CriadoEm


class RazaoSolicitacaoUnificado(Nomeavel):
    """
        a ideia é ser um combo de opcoes fixas
    """


class ItemKitLanche(Nomeavel):
    """
        Barra de Cereal (20 a 25 g embalagem individual)
        Néctar UHT ou Suco Tropical UHT (200 ml)
        Biscoito Integral Salgado (mín. de 25g embalagem individual)

        etc.
    """

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Item do kit lanche"
        verbose_name_plural = "Item do kit lanche"


class KitLanche(Nomeavel):
    """
        kit1, kit2, kit3
    """
    itens = models.ManyToManyField(ItemKitLanche)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Kit lanche"
        verbose_name_plural = "Kits lanche"


class SolicitacaoKitLanche(TemData, Motivo, Descritivel, CriadoEm):
    QUATRO = 0
    CINCO_A_SETE = 1
    OITO_OU_MAIS = 2

    HORAS = (
        (QUATRO, 'Quatro horas'),
        (CINCO_A_SETE, 'Cinco a sete horas'),
        (OITO_OU_MAIS, 'Oito horas'),
    )
    tempo_passeio = models.PositiveSmallIntegerField(choices=HORAS, default=QUATRO)
    kits = models.ManyToManyField(KitLanche)

    def __str__(self):
        return "{} criado em {}".format(self.motivo, self.criado_em)

    class Meta:
        verbose_name = "Kit lanche"
        verbose_name_plural = "Kits lanche"


class SolicitacaoKitLancheAvulsa(models.Model):
    local = models.CharField(max_length=160)
    quantidade_alunos = models.PositiveSmallIntegerField()
    dado_base = models.ForeignKey(SolicitacaoKitLanche, on_delete=models.DO_NOTHING)
    escola = models.ForeignKey('escola.Escola', on_delete=models.DO_NOTHING)

    def __str__(self):
        return "{} SOLICITA PARA {} ALUNOS EM {}".format(self.escola, self.quantidade_alunos, self.local)

    class Meta:
        verbose_name = "Solicitação de kit lanche avulsa"
        verbose_name_plural = "Solicitações de kit lanche avulsa"
