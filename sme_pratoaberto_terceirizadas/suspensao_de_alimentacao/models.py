import uuid

from django.core.validators import validate_comma_separated_integer_list
from django.db import models

from sme_pratoaberto_terceirizadas.common_data.utils import get_working_days_after
from sme_pratoaberto_terceirizadas.food.models import MealType
from sme_pratoaberto_terceirizadas.escola.models import PeriodoEscolar
from sme_pratoaberto_terceirizadas.users.models import User
from sme_pratoaberto_terceirizadas.meal_kit.utils import string_to_date


class StatusSuspensaoDeAlimentacao(models.Model):
    nome = models.CharField("Nome", blank=True, null=True, max_length=50)

    """Status da Suspensão de Alimentação"""

    SALVO = "SALVO"
    A_VALIDAR = "A VALIDAR"
    A_APROVAR = "A APROVAR"
    A_EDITAR = "A EDITAR"
    A_VISUALIZAR = "A VISUALIZAR"
    NEGADO_PELA_CODAE = "NEGADO PELA CODAE"
    NEGADO_PELA_TERCEIRIZADA = "NEGADO PELA TERCEIRIZADA"
    VISUALIZADO = "VISUALIZADO"

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Status"
        verbose_name_plural = "Status"


class RazaoSuspensaoDeAlimentacao(models.Model):
    nome = models.CharField("Nome", blank=True, null=True, max_length=50)
    """Motivo para Suspensão de Alimentação"""

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Razão"
        verbose_name_plural = "Razões"


class SuspensaoDeAlimentacao(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    criado_por = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    status = models.ForeignKey(StatusSuspensaoDeAlimentacao, on_delete=models.DO_NOTHING)
    negado_pela_terceirizada = models.BooleanField(default=False)
    razao_negacao = models.TextField(blank=True, null=True)
    obs = models.TextField(blank=True, null=True)

    def __str__(self):
        return '{nome} - {id}'.format(nome=self.status.nome, id=self.id)

    @classmethod
    def salvar_suspensao(cls, data, usuario):
        try:
            if data.get('id', None):
                obj = cls.objects.get(pk=data.get('id'))
                obj.dias_razoes.all().delete()
                obj.descricoes.all().delete()
            else:
                obj = cls()
            obj.criado_por = usuario
            if data.get('status', None):
                obj.status = StatusSuspensaoDeAlimentacao.objects.get(nome=data.get('status'))
            else:
                obj.status = StatusSuspensaoDeAlimentacao.objects.get(nome=StatusSuspensaoDeAlimentacao.SALVO)
            obj.negado_pela_terceirizada = data.get('negado_pela_terceirizada', False)
            if obj.negado_pela_terceirizada:
                obj.razao_negacao = data.get('razao_negacao')
            obj.obs = data.get('obs', None)
            obj.save()
            dias_razoes = data.get('dias_razoes')
            for dia_razao in dias_razoes:
                DiaRazaoSuspensaoDeAlimentacao.salvar_dias_razoes(dia_razao, obj)
            descricoes = data.get('descricoes')
            for descricao in descricoes:
                DescricaoSuspensaoDeAlimentacao.salvar_descricoes(descricao, obj)
            return obj
        except ValueError as e:
            print(e)
            return False


class DiaRazaoSuspensaoDeAlimentacao(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    suspensao_de_alimentacao = models.ForeignKey(SuspensaoDeAlimentacao, on_delete=models.CASCADE,
                                                 related_name="dias_razoes")
    razao = models.ForeignKey(RazaoSuspensaoDeAlimentacao, on_delete=models.DO_NOTHING)
    qual_razao = models.TextField(blank=True, null=True)
    prioridade = models.BooleanField(default=False)
    data = models.DateField(blank=True, null=True)
    data_de = models.DateField(blank=True, null=True)
    data_ate = models.DateField(blank=True, null=True)
    dias_de_semana = models.CharField(blank=True, null=True, max_length=14,
                                      validators=[validate_comma_separated_integer_list])

    def __str__(self):
        if self.data:
            return '{data} - {razao}'.format(razao=self.razao.nome, data=self.data)
        else:
            return '{data_de} - {data_ate} - {razao}'.format(data_de=self.data_de, data_ate=self.data_ate,
                                                             razao=self.razao.nome)

    @classmethod
    def salvar_dias_razoes(cls, data, suspensao):
        obj = cls()
        obj.suspensao_de_alimentacao = suspensao
        obj.razao = RazaoSuspensaoDeAlimentacao.objects.get(nome=data.get('razao'))
        obj.qual_razao = data.get('qual_razao', None)
        if data.get('data', None):
            obj.data = string_to_date(data.get('data'))
            obj.priority = get_working_days_after(days=2) <= obj.data <= get_working_days_after(days=5)
        else:
            obj.data_de = string_to_date(data.get('data_de'))
            obj.data_ate = string_to_date(data.get('data_ate'))
            obj.dias_de_semana = ",".join(data.get('dias_de_semana'))
        obj.save()
        return obj


class DescricaoSuspensaoDeAlimentacao(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    periodo = models.ForeignKey(PeriodoEscolar, on_delete=models.DO_NOTHING)
    tipo_de_refeicao = models.ManyToManyField(MealType)
    numero_de_alunos = models.IntegerField()
    suspensao_de_alimentacao = models.ForeignKey(SuspensaoDeAlimentacao, on_delete=models.CASCADE,
                                                 related_name="descricoes")

    def __str__(self):
        return '{nome} - {numero_de_alunos}'.format(nome=self.periodo.name,
                                                    numero_de_alunos=str(self.numero_de_alunos))

    @classmethod
    def salvar_descricoes(cls, data, suspensao):
        obj = cls()
        obj.suspensao_de_alimentacao = suspensao
        obj.periodo = PeriodoEscolar.objects.get(value=data.get('periodo'))
        obj.numero_de_alunos = data.get('numero_de_alunos')
        obj.save()
        tipos_de_refeicao = data.get('tipo_de_refeicao')
        for tipo_de_refeicao in tipos_de_refeicao:
            obj.tipo_de_refeicao.add(MealType.objects.get(name=tipo_de_refeicao))
        obj.save()
