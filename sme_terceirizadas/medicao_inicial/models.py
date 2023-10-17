import datetime
from calendar import monthcalendar, setfirstweekday

import numpy
from django.db import models

from ..dados_comuns.behaviors import (
    Ativavel,
    CriadoEm,
    CriadoPor,
    Logs,
    Nomeavel,
    Posicao,
    TemAlteradoEm,
    TemAno,
    TemChaveExterna,
    TemData,
    TemDia,
    TemIdentificadorExternoAmigavel,
    TemMes,
    TemSemana
)
from ..dados_comuns.fluxo_status import FluxoSolicitacaoMedicaoInicial, LogSolicitacoesUsuario
from ..escola.models import TipoUnidadeEscolar
from ..perfil.models import Usuario


class DiaSobremesaDoce(TemData, TemChaveExterna, CriadoEm, CriadoPor):
    tipo_unidade = models.ForeignKey(TipoUnidadeEscolar, on_delete=models.CASCADE)

    @property
    def tipo_unidades(self):
        return None

    def __str__(self):
        return f'{self.data.strftime("%d/%m/%Y")} - {self.tipo_unidade.iniciais}'

    class Meta:
        verbose_name = 'Dia de sobremesa doce'
        verbose_name_plural = 'Dias de sobremesa doce'
        unique_together = ('tipo_unidade', 'data',)
        ordering = ('data',)


class SolicitacaoMedicaoInicial(
    TemChaveExterna,
    TemIdentificadorExternoAmigavel,
    CriadoEm, CriadoPor,
    TemMes, TemAno,
    FluxoSolicitacaoMedicaoInicial,
    Logs,
):
    escola = models.ForeignKey('escola.Escola', on_delete=models.CASCADE,
                               related_name='solicitacoes_medicao_inicial')
    tipo_contagem_alimentacoes = models.ForeignKey('TipoContagemAlimentacao', on_delete=models.SET_NULL,
                                                   null=True, related_name='solicitacoes_medicao_inicial')
    com_ocorrencias = models.BooleanField('Com ocorrências?', default=False)
    historico = models.JSONField(blank=True, null=True)
    ue_possui_alunos_periodo_parcial = models.BooleanField('Possui alunos periodo parcial?', default=False)
    logs_salvos = models.BooleanField('Logs de matriculados, dietas autorizadas, etc foram salvos?', default=False)

    def salvar_log_transicao(self, status_evento, usuario, **kwargs):
        LogSolicitacoesUsuario.objects.create(
            descricao=str(self),
            status_evento=status_evento,
            solicitacao_tipo=LogSolicitacoesUsuario.MEDICAO_INICIAL,
            usuario=usuario,
            uuid_original=self.uuid,
        )

    @property
    def tem_ocorrencia(self):
        return hasattr(self, 'ocorrencia')

    class Meta:
        verbose_name = 'Solicitação de medição inicial'
        verbose_name_plural = 'Solicitações de medição inicial'
        unique_together = ('escola', 'mes', 'ano',)
        ordering = ('-ano', '-mes')

    def __str__(self):
        return f'Solicitação #{self.id_externo} -- Escola {self.escola.nome} -- {self.mes}/{self.ano}'


class OcorrenciaMedicaoInicial(TemChaveExterna, Logs, FluxoSolicitacaoMedicaoInicial):
    """Modelo para mapear a tabela Ocorrência e salvar objetos ocorrêcia da medição inicial."""

    nome_ultimo_arquivo = models.CharField(max_length=100)
    ultimo_arquivo = models.FileField()
    solicitacao_medicao_inicial = models.OneToOneField(
        SolicitacaoMedicaoInicial,
        on_delete=models.CASCADE,
        related_name='ocorrencia',
        blank=True, null=True
    )

    def salvar_log_transicao(self, status_evento, usuario, **kwargs):
        justificativa = kwargs.get('justificativa', '')
        log_transicao = LogSolicitacoesUsuario.objects.create(
            descricao=str(self),
            justificativa=justificativa,
            status_evento=status_evento,
            solicitacao_tipo=LogSolicitacoesUsuario.MEDICAO_INICIAL,
            usuario=usuario,
            uuid_original=self.uuid,
        )
        return log_transicao

    def deletar_log_correcao(self, status_evento, **kwargs):
        log = self.logs.last()
        if log and log.status_evento in status_evento:
            log.delete()

    def __str__(self):
        return f'Ocorrência {self.uuid} da Solicitação de Medição Inicial {self.solicitacao_medicao_inicial.uuid}'


class Responsavel(models.Model):
    nome = models.CharField('Nome', max_length=100)
    rf = models.CharField(max_length=10)
    solicitacao_medicao_inicial = models.ForeignKey(
        SolicitacaoMedicaoInicial,
        related_name='responsaveis',
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f'Responsável {self.nome} - {self.rf}'


class TipoContagemAlimentacao(Nomeavel, TemChaveExterna, Ativavel):

    class Meta:
        verbose_name = 'Tipo de contagem das alimentações'
        verbose_name_plural = 'Tipos de contagem das alimentações'

    def __str__(self):
        return self.nome


class GrupoMedicao(Nomeavel, TemChaveExterna, Ativavel):

    class Meta:
        verbose_name = 'Grupo de medição'
        verbose_name_plural = 'Grupos de medição'

    def __str__(self):
        return self.nome


class Medicao(
    TemChaveExterna,
    TemIdentificadorExternoAmigavel,
    FluxoSolicitacaoMedicaoInicial,
    CriadoEm, CriadoPor, Logs
):
    solicitacao_medicao_inicial = models.ForeignKey('SolicitacaoMedicaoInicial', on_delete=models.CASCADE,
                                                    related_name='medicoes')
    periodo_escolar = models.ForeignKey('escola.PeriodoEscolar', blank=True, null=True, on_delete=models.DO_NOTHING)
    grupo = models.ForeignKey(GrupoMedicao, blank=True, null=True, on_delete=models.PROTECT)
    alterado_em = models.DateTimeField('Alterado em', null=True, blank=True)

    def deletar_log_correcao(self, status_evento, **kwargs):
        log = self.logs.last()
        if log and log.status_evento in status_evento:
            log.delete()

    def salvar_log_transicao(self, status_evento, usuario, **kwargs):
        justificativa = kwargs.get('justificativa', '')
        LogSolicitacoesUsuario.objects.create(
            descricao=str(self),
            justificativa=justificativa,
            status_evento=status_evento,
            solicitacao_tipo=LogSolicitacoesUsuario.MEDICAO_INICIAL,
            usuario=usuario,
            uuid_original=self.uuid,
        )

    @property
    def nome_periodo_grupo(self):
        if self.grupo and self.periodo_escolar:
            nome_periodo_grupo = f'{self.grupo.nome} - ' + f'{self.periodo_escolar.nome}'
        elif self.grupo and not self.periodo_escolar:
            nome_periodo_grupo = f'{self.grupo.nome}'
        else:
            nome_periodo_grupo = f'{self.periodo_escolar.nome}'
        return nome_periodo_grupo

    class Meta:
        verbose_name = 'Medição'
        verbose_name_plural = 'Medições'

    def __str__(self):
        ano = f'{self.solicitacao_medicao_inicial.ano}'
        mes = f'{self.solicitacao_medicao_inicial.mes}'

        return f'Medição #{self.id_externo} -- {self.nome_periodo_grupo} -- {mes}/{ano}'


class CategoriaMedicao(Nomeavel, Ativavel, TemChaveExterna):

    class Meta:
        verbose_name = 'Categoria de medição'
        verbose_name_plural = 'Categorias de medições'

    def __str__(self):
        return self.nome


class ValorMedicao(
    TemChaveExterna,
    TemIdentificadorExternoAmigavel,
    CriadoEm, TemDia, TemSemana
):
    valor = models.TextField('Valor do Campo')
    nome_campo = models.CharField(max_length=100)
    medicao = models.ForeignKey('Medicao', on_delete=models.CASCADE, related_name='valores_medicao')
    categoria_medicao = models.ForeignKey('CategoriaMedicao', on_delete=models.CASCADE,
                                          related_name='valores_medicao')
    tipo_alimentacao = models.ForeignKey('cardapio.TipoAlimentacao', blank=True,
                                         null=True, on_delete=models.DO_NOTHING)
    faixa_etaria = models.ForeignKey('escola.FaixaEtaria', blank=True,
                                     null=True, on_delete=models.DO_NOTHING)
    habilitado_correcao = models.BooleanField(default=False)

    @classmethod
    def get_week_of_month(cls, year, month, day):
        setfirstweekday(0)
        x = numpy.array(monthcalendar(year, month))
        week_of_month = numpy.where(x == day)[0][0] + 1
        return week_of_month

    def __str__(self):
        categoria = f'{self.categoria_medicao.nome}'
        nome_campo = f'{self.nome_campo}'
        dia = f'{self.dia}'
        mes = f'{self.medicao.solicitacao_medicao_inicial.mes}'
        return f'#{self.id_externo} -- Categoria {categoria} -- Campo {nome_campo} -- Dia/Mês {dia}/{mes}'

    class Meta:
        verbose_name = 'Valor da Medição'
        verbose_name_plural = 'Valores das Medições'


class AlimentacaoLancamentoEspecial(Nomeavel, Ativavel, TemChaveExterna, Posicao):

    class Meta:
        verbose_name = 'Alimentação de Lançamento Especial'
        verbose_name_plural = 'Alimentações de Lançamentos Especiais'
        ordering = ['posicao']

    def __str__(self):
        return self.nome


class PermissaoLancamentoEspecial(CriadoPor, CriadoEm, TemAlteradoEm, TemChaveExterna, TemIdentificadorExternoAmigavel):
    escola = models.ForeignKey('escola.Escola', on_delete=models.CASCADE, related_name='permissoes_lancamento_especial')
    periodo_escolar = models.ForeignKey('escola.PeriodoEscolar', blank=True, null=True, on_delete=models.DO_NOTHING)
    alimentacoes_lancamento_especial = models.ManyToManyField(AlimentacaoLancamentoEspecial)
    diretoria_regional = models.ForeignKey('escola.DiretoriaRegional', related_name='permissoes_lancamento_especial',
                                           on_delete=models.DO_NOTHING)
    data_inicial = models.DateField('Data inicial', null=True, blank=True)
    data_final = models.DateField('Data final', null=True, blank=True)

    @property
    def ativo(self):
        hoje = datetime.datetime.today().date()
        if self.data_inicial and self.data_final:
            return self.data_inicial <= hoje <= self.data_final
        if self.data_inicial and not self.data_final:
            return self.data_inicial <= hoje
        if not self.data_inicial and self.data_final:
            return hoje <= self.data_final
        if not self.data_inicial and not self.data_final:
            return True

    class Meta:
        verbose_name = 'Permissão de Lançamento Especial'
        verbose_name_plural = 'Permissões de Lançamentos Especiais'
        ordering = ['-alterado_em']

    def __str__(self):
        return f'Permissão #{self.id_externo} - {self.escola.nome}'


class DiaParaCorrigir(TemChaveExterna, TemIdentificadorExternoAmigavel, TemDia, CriadoEm, CriadoPor):
    medicao = models.ForeignKey('Medicao', on_delete=models.CASCADE, related_name='dias_para_corrigir')
    categoria_medicao = models.ForeignKey(
        'CategoriaMedicao', on_delete=models.CASCADE, related_name='dias_para_corrigir')
    habilitado_correcao = models.BooleanField(default=True)

    @classmethod
    def cria_dias_para_corrigir(cls, medicao: Medicao, usuario: Usuario, list_dias_para_corrigir: list) -> None:
        if not list_dias_para_corrigir:
            return
        medicao.dias_para_corrigir.all().delete()
        list_dias_para_corrigir_a_criar = []
        for dia_para_corrigir in list_dias_para_corrigir:
            categoria_medicao = CategoriaMedicao.objects.get(uuid=dia_para_corrigir['categoria_medicao_uuid'])
            dia_obj = DiaParaCorrigir(
                medicao=medicao,
                dia=dia_para_corrigir['dia'],
                categoria_medicao=categoria_medicao,
                criado_por=usuario
            )
            list_dias_para_corrigir_a_criar.append(dia_obj)
        DiaParaCorrigir.objects.bulk_create(list_dias_para_corrigir_a_criar)

    def __str__(self):
        escola = self.medicao.solicitacao_medicao_inicial.escola.nome
        periodo_ou_grupo = self.medicao.grupo.nome if self.medicao.grupo else self.medicao.periodo_escolar.nome
        mes = self.medicao.solicitacao_medicao_inicial.mes
        ano = self.medicao.solicitacao_medicao_inicial.ano
        return f'# {self.id_externo} - {escola} - {periodo_ou_grupo} - {self.dia}/{mes}/{ano}'

    class Meta:
        verbose_name = 'Dia da Medição para corrigir'
        verbose_name_plural = 'Dias da Medição para corrigir'
