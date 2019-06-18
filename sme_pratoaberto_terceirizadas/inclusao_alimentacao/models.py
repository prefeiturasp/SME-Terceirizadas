import uuid

from django.core.validators import validate_comma_separated_integer_list
from django.db import models
from django.utils.translation import ugettext as _
from notifications.signals import notify

from sme_pratoaberto_terceirizadas.abstract_shareable import Descritivel, RegistroHora, Ativavel
from sme_pratoaberto_terceirizadas.common_data.utils import str_to_date, obter_dias_uteis_apos
from sme_pratoaberto_terceirizadas.alimento.models import TipoRefeicao
from sme_pratoaberto_terceirizadas.inclusao_alimentacao.utils import obter_objeto
from sme_pratoaberto_terceirizadas.escola.models import PeriodoEscolar
from sme_pratoaberto_terceirizadas.users.models import User


class InclusaoAlimentacaoStatus(Descritivel):
    """Status da Inclusão de Alimentação"""

    SALVO = "SALVO"
    A_VALIDAR = _('A_VALIDAR')
    A_APROVAR = _('A_APROVAR')
    A_EDITAR = _('A_EDITAR')
    A_VISUALIZAR = _('A_VISUALIZAR')
    NEGADO_PELA_CODAE = _('NEGADO_PELA_CODAE')
    NEGADO_PELA_TERCEIRIZADA = _('NEGADO_PELA_TERCEIRIZADA')
    VISUALIZADO = _('VISUALIZADO')

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = _("Status")
        verbose_name_plural = _("Status")


class MotivoInclusaoAlimentacao(Descritivel, Ativavel):
    """Motivo para Inclusão de Alimentação"""

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = _("Motivo")
        verbose_name_plural = _("Motivos")


class InclusaoAlimentacao(RegistroHora):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    criado_por = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    status = models.ForeignKey(InclusaoAlimentacaoStatus, on_delete=models.DO_NOTHING)
    negado_pela_terceirizada = models.BooleanField(default=False)
    motivo_recusa = models.TextField(blank=True, null=True)
    observacao = models.TextField(blank=True, null=True)

    def __str__(self):
        return '{nome} - {id}'.format(name=self.status.nome, id=self.id)

    class Meta:
        verbose_name = _("Inclusao Alimentacao")
        verbose_name_plural = _("Inclusao Alimentacões")

    def criar_ou_alterar(self, request_data, user):
        self._set_status(request_data)
        self.criado_por = user
        self.observacao = request_data.get('observacao', None)
        self.save()
        self._criar_ou_alterar_dia_motivos(request_data)
        self._criar_ou_alterar_descricoes(request_data)

    def _criar_ou_alterar_dia_motivos(self, request_data):
        dia_motivos = request_data.get('dia_motivos')
        for dia_motivo in dia_motivos:
            dia_motivo_uuid = dia_motivo.get('uuid', None)
            dia_motivo_inclusao_alimentacao = DiaMotivoInclusaoAlimentacao.objects.get(uuid=dia_motivo_uuid) \
                if dia_motivo_uuid else DiaMotivoInclusaoAlimentacao()
            dia_motivo_inclusao_alimentacao.criar_ou_alterar(dia_motivo, self)

    def _criar_ou_alterar_descricoes(self, request_data):
        descricoes = [request_data.get('descricao_primeiro_periodo', None),
                        request_data.get('descricao_segundo_periodo', None),
                        request_data.get('descricao_terceiro_periodo', None),
                        request_data.get('descricao_quarto_periodo', None),
                        request_data.get('descricao_integral', None)]
        for descricao in descricoes:
            if descricao:
                desc_uuid = descricao.get('uuid', None)
                food_inclusion_description = DescricaoInclusaoAlimentacao.objects.get(uuid=desc_uuid) \
                    if desc_uuid else DescricaoInclusaoAlimentacao()
                food_inclusion_description.criar_ou_alterar(descricao, self)

    def _set_status(self, request_data):
        status = request_data.get('status', None)
        nome = status if status else InclusaoAlimentacaoStatus.A_VALIDAR
        self.status = obter_objeto(InclusaoAlimentacaoStatus, name=nome)

    def _notificacao_aux(self, _type, validation_diff='creation'):
        notificacao_dict = {
            InclusaoAlimentacaoStatus.A_VALIDAR: {
                'receptor': User.objects.all(),
                'aviso': _(validation_diff.capitalize()),
                'descricao': _('created') if validation_diff else _('edited')
            },
            InclusaoAlimentacaoStatus.A_EDITAR: {
                'receptor': User.objects.all(),
                'aviso': _('Necessário editar'),
                'descricao': _('não válidado')
            },
            InclusaoAlimentacaoStatus.A_APROVAR: {
                'receptor': User.objects.all(),
                'aviso': _('Validação'),
                'descricao': _('validado')
            },
            InclusaoAlimentacaoStatus.A_VISUALIZAR: {
                'receptor': User.objects.all(),
                'aviso': _('Aprovação'),
                'descricao': _('aprovado')
            },
            InclusaoAlimentacaoStatus.NEGADO_PELA_CODAE: {
                'receptor': User.objects.all(),
                'aviso': _('Negado pela CODAE'),
                'descricao': _('negado pela CODAE')
            },
            InclusaoAlimentacaoStatus.NEGADO_PELA_TERCEIRIZADA_: {
                'receptor': User.objects.all(),
                'aviso': _('Negado pela Terceirizada'),
                'descricao': _('negada pela terceirizada')
            },
            InclusaoAlimentacaoStatus.VISUALIZADO: {
                'receptor': User.objects.all(),
                'aviso': _('Visualização'),
                'descricao': _('visualizado')
            },
        }
        return notificacao_dict[self.status.nome][_type]

    def enviar_notificacao(self, actor, validation_diff='creation'):
        notify.send(
            sender=actor,
            recipient=self._notificacao_aux('receptor', validation_diff),
            verb=_('Inclusao Alimentacao - ') + self._notificacao_aux('verb', validation_diff),
            action_object=self,
            description="O usuário" + actor.name + self._notificacao_aux('descricao', validation_diff) +
                        " uma inclusão de alimentação")


class DescricaoInclusaoAlimentacao(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    periodo = models.ForeignKey(PeriodoEscolar, on_delete=models.DO_NOTHING)
    tipo_refeicao = models.ManyToManyField(TipoRefeicao)
    numero_de_estudantes = models.IntegerField()
    inclusao_alimentacao = models.ForeignKey(InclusaoAlimentacao, related_name="descricoes", on_delete=models.CASCADE)

    def __str__(self):
        return '{nome} - {numero_de_estudantes}'.format(nome=self.periodo.name,
                                                      numero_de_estudantes=str(self.numero_de_estudantes))

    class Meta:
        verbose_name = _("Descrição de inclusão de alimentação")
        verbose_name_plural = _("Descrições de inclusão de alimentação")

    def criar_ou_atualizar(self, request_data, food_inclusion):
        periodo_escolar = request_data.get('value')
        tipo_refeicao = request_data.get('select') if isinstance(request_data.get('select'), list) else [
            request_data.get('select')]
        self.numero_de_estudantes = request_data.get('number')
        self.inclusao_alimentacao = food_inclusion
        self.periodo = obter_objeto(PeriodoEscolar, value=periodo_escolar)
        self.save()
        for refeicao in tipo_refeicao:
            self.tipo_refeicao.add(obter_objeto(TipoRefeicao, name=refeicao))
        self.save()


class DiaMotivoInclusaoAlimentacao(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    inclusao_alimentacao = models.ForeignKey(InclusaoAlimentacao, on_delete=models.CASCADE)
    motivo = models.ForeignKey(MotivoInclusaoAlimentacao,  related_name="motivos", on_delete=models.DO_NOTHING)
    descricao_motivo = models.TextField(blank=True, null=True)
    prioridade = models.BooleanField(default=False)
    data = models.DateField(blank=True, null=True)
    do_dia = models.DateField(blank=True, null=True)
    ate_dia = models.DateField(blank=True, null=True)
    dias_semana = models.CharField(blank=True, null=True, max_length=14,
                                validators=[validate_comma_separated_integer_list])

    def criar_ou_atualizar(self, request_data, inclusao_alimentacao):
        data = request_data.get('data', None)
        motivo = request_data.get('motivo')
        self.motivo = MotivoInclusaoAlimentacao.objects.get(name=motivo)
        self.descricao_motivo = request_data.get('descricao_motivo', None)
        self.inclusao_alimentacao = inclusao_alimentacao
        if data:
            self.data = str_to_date(data)
            self.prioridade = obter_dias_uteis_apos(days=2) <= self.data <= obter_dias_uteis_apos(days=5)
            self.do_dia = None
            self.ate_dia = None
            self.dias_semana = None
        else:
            self.data = None
            self.do_dia = str_to_date(request_data.get('do_dia'))
            self.ate_dia = str_to_date(request_data.get('ate_dia'))
            self.dias_semana = ",".join(request_data.get('dias_semana', None))
        self.save()
