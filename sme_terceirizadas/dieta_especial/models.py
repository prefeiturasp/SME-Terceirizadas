from django.core.validators import MinLengthValidator
from django.db import models
from django_prometheus.models import ExportModelOperationsMixin

from ..dados_comuns.behaviors import (
    Ativavel,
    CriadoEm,
    CriadoPor,
    Descritivel,
    Logs,
    Nomeavel,
    TemChaveExterna,
    TemIdentificadorExternoAmigavel,
    TemPrioridade
)
from ..dados_comuns.fluxo_status import FluxoDietaEspecialPartindoDaEscola
from ..dados_comuns.models import LogSolicitacoesUsuario, TemplateMensagem
from ..escola.api.serializers import AlunoSerializer
from ..escola.models import Aluno


class SolicitacaoDietaEspecial(ExportModelOperationsMixin('dieta_especial'), TemChaveExterna, CriadoEm, CriadoPor,
                               FluxoDietaEspecialPartindoDaEscola, TemPrioridade,
                               Logs, TemIdentificadorExternoAmigavel, Ativavel):
    DESCRICAO = 'Dieta Especial'
    aluno = models.ForeignKey('escola.Aluno', null=True, on_delete=models.PROTECT, related_name='dietas_especiais')
    nome_completo_pescritor = models.CharField('Nome completo do pescritor da receita',
                                               max_length=200,
                                               validators=[MinLengthValidator(6)],
                                               blank=True)
    registro_funcional_pescritor = models.CharField('Nome completo do pescritor da receita',
                                                    help_text='CRN/CRM/CRFa...',
                                                    max_length=200,
                                                    validators=[MinLengthValidator(6)],
                                                    blank=True)
    registro_funcional_nutricionista = models.CharField('Nome completo do pescritor da receita',
                                                        help_text='CRN/CRM/CRFa...',
                                                        max_length=200,
                                                        validators=[MinLengthValidator(6)],
                                                        blank=True)
    observacoes = models.TextField('Observações', blank=True)

    tipos = models.ManyToManyField('TipoDieta', blank=True)
    # TODO: Confirmar se PROTECT é a melhor escolha para o campos abaixo
    classificacao = models.ForeignKey('ClassificacaoDieta', blank=True, null=True, on_delete=models.PROTECT)
    alergias_intolerancias = models.ManyToManyField('AlergiaIntolerancia', blank=True)

    # TODO: Confirmar se PROTECT é a melhor escolha para o campos abaixo
    motivo_negacao = models.ForeignKey('MotivoNegacao', on_delete=models.PROTECT, null=True)
    justificativa_negacao = models.TextField(blank=True)

    # Property necessária para retornar dados no serializer de criação de Dieta Especial
    @property
    def aluno_json(self):
        return AlunoSerializer(self.aluno).data

    @property
    def anexos(self):
        return self.anexo_set.all()

    @property
    def escola(self):
        return self.rastro_escola

    @property
    def template_mensagem(self):
        template = TemplateMensagem.objects.get(tipo=TemplateMensagem.DIETA_ESPECIAL)
        template_troca = {
            '@id': self.id_externo,
            '@criado_em': str(self.criado_em),
            '@criado_por': str(self.criado_por),
            '@status': str(self.status),
            # TODO: verificar a url padrão do pedido
            '@link': 'http://teste.com',
        }
        corpo = template.template_html
        for chave, valor in template_troca.items():
            corpo = corpo.replace(chave, valor)
        return template.assunto, corpo

    def salvar_log_transicao(self, status_evento, usuario, **kwargs):
        justificativa = kwargs.get('justificativa', '')
        LogSolicitacoesUsuario.objects.create(
            descricao=str(self),
            status_evento=status_evento,
            solicitacao_tipo=LogSolicitacoesUsuario.DIETA_ESPECIAL,
            usuario=usuario,
            uuid_original=self.uuid,
            justificativa=justificativa
        )

    class Meta:
        ordering = ('-ativo', '-criado_em')
        verbose_name = 'Solicitação de dieta especial'
        verbose_name_plural = 'Solicitações de dieta especial'

    def __str__(self):
        if self.aluno:
            return f'{self.aluno.codigo_eol}: {self.aluno.nome}'
        return f'Solicitação #{self.id_externo}'


class Anexo(ExportModelOperationsMixin('anexo'), models.Model):
    solicitacao_dieta_especial = models.ForeignKey(SolicitacaoDietaEspecial, on_delete=models.DO_NOTHING)
    nome = models.CharField(max_length=100, blank=True)
    arquivo = models.FileField()
    eh_laudo_medico = models.BooleanField(default=False)

    def __str__(self):
        return self.nome


class AlergiaIntolerancia(Descritivel):
    def __str__(self):
        return self.descricao


class ClassificacaoDieta(Descritivel, Nomeavel):
    def __str__(self):
        return self.nome


class MotivoNegacao(Descritivel):
    def __str__(self):
        return self.descricao


class TipoDieta(Descritivel):
    def __str__(self):
        return self.descricao


class SolicitacoesDietaEspecialAtivasInativasPorAluno(models.Model):
    aluno = models.OneToOneField(Aluno, on_delete=models.DO_NOTHING, primary_key=True)
    ativas = models.IntegerField()
    inativas = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'dietas_ativas_inativas_por_aluno'
