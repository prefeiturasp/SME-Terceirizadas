from django.core.validators import MinLengthValidator
from django.db import models

from ..dados_comuns.models import LogSolicitacoesUsuario, TemplateMensagem
from ..dados_comuns.behaviors import CriadoEm, CriadoPor, Logs, TemChaveExterna, TemIdentificadorExternoAmigavel
from ..dados_comuns.fluxo_status import FluxoDietaEspecialPartindoDaEscola


class SolicitacaoDietaEspecial(TemChaveExterna, CriadoEm, CriadoPor, FluxoDietaEspecialPartindoDaEscola,
                               Logs, TemIdentificadorExternoAmigavel):
    codigo_eol_aluno = models.CharField('Código EOL do aluno',
                                        max_length=6,
                                        validators=[MinLengthValidator(6)])
    nome_completo_aluno = models.CharField('Nome completo do aluno',
                                           max_length=200,
                                           validators=[MinLengthValidator(6)])
    nome_completo_pescritor = models.CharField('Nome completo do pescritor da receita',
                                               max_length=200,
                                               validators=[MinLengthValidator(6)],
                                               blank=True,
                                               null=True)
    registro_funcional_pescritor = models.CharField('Nome completo do pescritor da receita',
                                                    help_text='CRN/CRM/CRFa...',
                                                    max_length=200,
                                                    validators=[MinLengthValidator(6)],
                                                    blank=True,
                                                    null=True)
    data_nascimento_aluno = models.DateField('Data de nascimento do aluno')

    observacoes = models.TextField('Observações', blank=True)

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
        verbose_name = 'Solicitação de dieta especial'
        verbose_name_plural = 'Solicitações de dieta especial'

    def __str__(self):
        return f'{self.codigo_eol_aluno}: {self.nome_completo_aluno}'


class Anexo(models.Model):
    solicitacao_dieta_especial = models.ForeignKey(SolicitacaoDietaEspecial, on_delete=models.DO_NOTHING)
    arquivo = models.FileField()

    @property
    def nome(self):
        return self.arquivo.url
