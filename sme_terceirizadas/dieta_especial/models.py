from django.core.validators import MinLengthValidator
from django.db import models

from ..dados_comuns.behaviors import CriadoEm, CriadoPor, TemChaveExterna


class SolicitacaoDietaEspecial(TemChaveExterna, CriadoEm, CriadoPor):
    codigo_eol_aluno = models.CharField('Código EOL do aluno',
                                        max_length=6,
                                        validators=[MinLengthValidator(6)])
    nome_completo_aluno = models.CharField('Nome completo do aluno',
                                           max_length=200,
                                           validators=[MinLengthValidator(6)])
    nome_completo_pescritor = models.CharField('Nome completo do pescritor da receita',
                                               max_length=200,
                                               validators=[MinLengthValidator(6)])
    registro_funcional_pescritor = models.CharField('Nome completo do pescritor da receita',
                                                    help_text='CRN/CRM/CRFa...',
                                                    max_length=200,
                                                    validators=[MinLengthValidator(6)])
    data_nascimento_aluno = models.DateField('Data de nascimento do aluno')

    observacoes = models.TextField('Observações', blank=True)

    @property
    def anexos(self):
        return self.anexo_set.all()

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
