from django.db import models

from ..dados_comuns.models_abstract import (
    Nomeavel, TemData, Motivo, Descritivel,
    CriadoEm, TemChaveExterna, TempoPasseio, CriadoPor,
    FluxoAprovacaoPartindoDaEscola, TemIdentificadorExternoAmigavel,
    FluxoAprovacaoPartindoDaDiretoriaRegional)


class MotivoSolicitacaoUnificada(Nomeavel, TemChaveExterna):
    """
        a ideia é ser um combo de opcoes fixas
    """

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Motivo da solicitação unificada"
        verbose_name_plural = "Motivos da solicitação unificada"


class ItemKitLanche(Nomeavel, TemChaveExterna):
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


class KitLanche(Nomeavel, TemChaveExterna):
    """
        kit1, kit2, kit3
    """
    itens = models.ManyToManyField(ItemKitLanche)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Kit lanche"
        verbose_name_plural = "Kit lanches"


class SolicitacaoKitLanche(TemData, Motivo, Descritivel, CriadoEm, TempoPasseio, TemChaveExterna):
    # TODO: implementar one to one, nas duas tabelas que apontam pra essa
    # https://docs.djangoproject.com/en/2.2/ref/models/fields/#django.db.models.OneToOneField

    kits = models.ManyToManyField(KitLanche, blank=True)

    def __str__(self):
        return "{} criado em {}".format(self.motivo, self.criado_em)

    class Meta:
        verbose_name = "Solicitação kit lanche base"
        verbose_name_plural = "Solicitações kit lanche base"


class SolicitacaoKitLancheAvulsa(TemChaveExterna, FluxoAprovacaoPartindoDaEscola):
    # TODO: ao deletar este, deletar solicitacao_kit_lanche também que é uma tabela acessória
    # TODO: passar `local` para solicitacao_kit_lanche
    local = models.CharField(max_length=160)
    quantidade_alunos = models.PositiveSmallIntegerField()
    solicitacao_kit_lanche = models.ForeignKey(SolicitacaoKitLanche, on_delete=models.DO_NOTHING)
    escola = models.ForeignKey('escola.Escola', on_delete=models.DO_NOTHING,
                               related_name='solicitacoes_kit_lanche_avulsa')

    def __str__(self):
        return "{} SOLICITA PARA {} ALUNOS EM {}".format(self.escola, self.quantidade_alunos, self.local)

    class Meta:
        verbose_name = "Solicitação de kit lanche avulsa"
        verbose_name_plural = "Solicitações de kit lanche avulsa"


class SolicitacaoKitLancheUnificada(CriadoPor, TemChaveExterna, TemIdentificadorExternoAmigavel,
                                    FluxoAprovacaoPartindoDaDiretoriaRegional):
    """
        significa que uma DRE vai pedir kit lanche para as escolas:

        lista_kit_lanche_igual é a mesma lista de kit lanche pra todos.
        não lista_kit_lanche_igual: cada escola tem sua lista de kit lanche

        QUANDO É lista_kit_lanche_igual: ex: passeio pra escola x,y,z no ibira (local)
        no dia 26 onde a escola x vai ter 100 alunos, a y 50 e a z 77 alunos.
        onde todos vao comemorar o dia da arvore (motivo)
    """
    # TODO: ao deletar este, deletar solicitacao_kit_lanche também que é uma tabela acessória
    # TODO: passar `local` para solicitacao_kit_lanche
    motivo = models.ForeignKey(MotivoSolicitacaoUnificada, on_delete=models.DO_NOTHING,
                               blank=True, null=True)
    outro_motivo = models.TextField(blank=True, null=True)
    quantidade_max_alunos_por_escola = models.PositiveSmallIntegerField(null=True, blank=True)
    local = models.CharField(max_length=160)
    lista_kit_lanche_igual = models.BooleanField(default=True)

    diretoria_regional = models.ForeignKey('escola.DiretoriaRegional', on_delete=models.DO_NOTHING)
    solicitacao_kit_lanche = models.ForeignKey(SolicitacaoKitLanche, on_delete=models.DO_NOTHING)

    def vincula_escolas_quantidades(self, escolas_quantidades):
        for escola_quantidade in escolas_quantidades:
            escola_quantidade.solicitacao_unificada = self
            escola_quantidade.save()

    def __str__(self):
        return "{} pedindo passeio em {} com kits iguais? {}".format(
            self.diretoria_regional,
            self.local,
            self.lista_kit_lanche_igual)

    class Meta:
        verbose_name = "Solicitação kit lanche unificada"
        verbose_name_plural = "Solicitações de  kit lanche unificadas"


class EscolaQuantidade(TemChaveExterna, TempoPasseio):
    quantidade_alunos = models.PositiveSmallIntegerField()
    solicitacao_unificada = models.ForeignKey(SolicitacaoKitLancheUnificada,
                                              on_delete=models.CASCADE,
                                              related_name='escolas_quantidades',
                                              blank=True, null=True)
    kits = models.ManyToManyField(KitLanche, blank=True)
    escola = models.ForeignKey('escola.Escola', on_delete=models.DO_NOTHING)

    def __str__(self):
        kit_lanche_personalizado = bool(self.kits.count())
        return "{} para {} alunos, kits diferenciados? {}".format(
            self.get_tempo_passeio_display(),
            self.quantidade_alunos,
            kit_lanche_personalizado)

    class Meta:
        verbose_name = "Escola quantidade"
        verbose_name_plural = "Escolas quantidades"
