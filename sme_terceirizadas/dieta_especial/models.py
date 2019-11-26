from django.core.validators import MinLengthValidator
from django.db import models

# from ..dados_comuns.behaviors import TemChaveExterna
from sme_terceirizadas.dados_comuns.behaviors import TemChaveExterna


class SolicitacaoDietaEspecial(TemChaveExterna):
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
    observacoes = models.TextField('Observações', null=True, blank=True)

    class Meta:
        verbose_name = 'Solicitação de dieta especial'
        verbose_name_plural = 'Solicitações de dieta especial'

    def __str__(self):
        return f'{self.codigo_eol_aluno}: {self.nome_completo_aluno}'
