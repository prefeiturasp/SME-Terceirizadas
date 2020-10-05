from django.core.validators import MaxLengthValidator, MinLengthValidator
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
from ..dados_comuns.utils import convert_base64_to_contentfile
from ..dados_comuns.validators import nao_pode_ser_no_passado
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
                                                    validators=[MinLengthValidator(4), MaxLengthValidator(6)],
                                                    blank=True)
    registro_funcional_nutricionista = models.CharField('Nome completo do pescritor da receita',
                                                        help_text='CRN/CRM/CRFa...',
                                                        max_length=200,
                                                        validators=[MinLengthValidator(6)],
                                                        blank=True)
    # Preenchido pela Escola
    observacoes = models.TextField('Observações', blank=True)
    # Preenchido pela CODAE ao autorizar a dieta
    informacoes_adicionais = models.TextField('Informações Adicionais', blank=True)
    nome_protocolo = models.TextField('Nome do Protocolo', blank=True)

    # TODO: Confirmar se PROTECT é a melhor escolha para o campos abaixo
    classificacao = models.ForeignKey('ClassificacaoDieta', blank=True, null=True, on_delete=models.PROTECT)
    alergias_intolerancias = models.ManyToManyField('AlergiaIntolerancia', blank=True)

    # TODO: Confirmar se PROTECT é a melhor escolha para o campos abaixo
    motivo_negacao = models.ForeignKey('MotivoNegacao', on_delete=models.PROTECT, null=True)
    # TODO: Mover essa justificativa para o log de transição de status
    justificativa_negacao = models.TextField(blank=True)

    data_termino = models.DateField(null=True, validators=[nao_pode_ser_no_passado])

    @classmethod
    def aluno_possui_dieta_especial_pendente(cls, aluno):
        return cls.objects.filter(aluno=aluno,
                                  status=cls.workflow_class.CODAE_A_AUTORIZAR).exists()

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

    def cria_anexos_inativacao(self, anexos):
        assert isinstance(anexos, list), 'anexos precisa ser uma lista'
        assert len(anexos) > 0, 'anexos não pode ser vazio'
        for anexo in anexos:
            data = convert_base64_to_contentfile(anexo.get('arquivo'))
            Anexo.objects.create(
                solicitacao_dieta_especial=self, arquivo=data, nome=anexo.get('nome', ''),
                eh_laudo_alta=True
            )

    @property
    def substituicoes(self):
        return self.substituicaoalimento_set.all()

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
    solicitacao_dieta_especial = models.ForeignKey(SolicitacaoDietaEspecial, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100, blank=True)
    arquivo = models.FileField()
    eh_laudo_alta = models.BooleanField(default=False)

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


class SolicitacoesDietaEspecialAtivasInativasPorAluno(models.Model):
    aluno = models.OneToOneField(Aluno, on_delete=models.DO_NOTHING, primary_key=True)
    ativas = models.IntegerField()
    inativas = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'dietas_ativas_inativas_por_aluno'


class Alimento(Nomeavel):
    def __str__(self):
        return self.nome


class SubstituicaoAlimento(models.Model):
    TIPO_CHOICES = [
        ('I', 'Isento'),
        ('S', 'Substituir')
    ]

    solicitacao_dieta_especial = models.ForeignKey(SolicitacaoDietaEspecial, on_delete=models.CASCADE)
    alimento = models.ForeignKey(Alimento, on_delete=models.PROTECT, blank=True, null=True)
    tipo = models.CharField(max_length=1, choices=TIPO_CHOICES, blank=True)
    substitutos = models.ManyToManyField('produto.Produto', related_name='substitutos', blank=True)


class TipoContagem(Nomeavel, TemChaveExterna):
    def __str__(self):
        return self.nome
