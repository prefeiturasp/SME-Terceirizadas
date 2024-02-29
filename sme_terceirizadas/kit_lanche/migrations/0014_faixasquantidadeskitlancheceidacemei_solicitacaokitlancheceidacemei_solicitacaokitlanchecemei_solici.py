# Generated by Django 2.2.13 on 2022-09-17 00:10

import uuid

import django.db.models.deletion
import django_xworkflows.models
from django.conf import settings
from django.db import migrations, models

import sme_terceirizadas.dados_comuns.behaviors


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("terceirizada", "0007_auto_20211008_1027"),
        ("escola", "0053_periodoescolar_tipo_turno"),
        ("kit_lanche", "0013_auto_20220720_1108"),
    ]

    operations = [
        migrations.CreateModel(
            name="SolicitacaoKitLancheCEMEI",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "criado_em",
                    models.DateTimeField(auto_now_add=True, verbose_name="Criado em"),
                ),
                (
                    "uuid",
                    models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
                ),
                ("observacao", models.TextField(blank=True, verbose_name="Observação")),
                (
                    "foi_solicitado_fora_do_prazo",
                    models.BooleanField(
                        default=False,
                        verbose_name="Solicitação foi criada em cima da hora (5 dias úteis ou menos)?",
                    ),
                ),
                (
                    "terceirizada_conferiu_gestao",
                    models.BooleanField(
                        default=False, verbose_name="Terceirizada conferiu?"
                    ),
                ),
                (
                    "status",
                    django_xworkflows.models.StateField(
                        max_length=37,
                        workflow=django_xworkflows.models._SerializedWorkflow(
                            initial_state="RASCUNHO",
                            name="PedidoAPartirDaEscolaWorkflow",
                            states=[
                                "RASCUNHO",
                                "DRE_A_VALIDAR",
                                "DRE_VALIDADO",
                                "DRE_PEDIU_ESCOLA_REVISAR",
                                "DRE_NAO_VALIDOU_PEDIDO_ESCOLA",
                                "CODAE_AUTORIZADO",
                                "CODAE_QUESTIONADO",
                                "CODAE_NEGOU_PEDIDO",
                                "TERCEIRIZADA_RESPONDEU_QUESTIONAMENTO",
                                "TERCEIRIZADA_TOMOU_CIENCIA",
                                "ESCOLA_CANCELOU",
                                "CANCELADO_AUTOMATICAMENTE",
                            ],
                        ),
                    ),
                ),
                ("local", models.CharField(max_length=160)),
                ("data", models.DateField(verbose_name="Data")),
                (
                    "alunos_cei_e_ou_emei",
                    models.CharField(
                        choices=[("TODOS", "Todos"), ("CEI", "CEI"), ("EMEI", "EMEI")],
                        default="TODOS",
                        max_length=10,
                    ),
                ),
                (
                    "criado_por",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "escola",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="solicitacoes_kit_lanche_cemei",
                        to="escola.Escola",
                    ),
                ),
                (
                    "rastro_dre",
                    models.ForeignKey(
                        blank=True,
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="kit_lanche_solicitacaokitlanchecemei_rastro_dre",
                        to="escola.DiretoriaRegional",
                    ),
                ),
                (
                    "rastro_escola",
                    models.ForeignKey(
                        blank=True,
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="kit_lanche_solicitacaokitlanchecemei_rastro_escola",
                        to="escola.Escola",
                    ),
                ),
                (
                    "rastro_lote",
                    models.ForeignKey(
                        blank=True,
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="kit_lanche_solicitacaokitlanchecemei_rastro_lote",
                        to="escola.Lote",
                    ),
                ),
                (
                    "rastro_terceirizada",
                    models.ForeignKey(
                        blank=True,
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="kit_lanche_solicitacaokitlanchecemei_rastro_terceirizada",
                        to="terceirizada.Terceirizada",
                    ),
                ),
            ],
            options={
                "verbose_name": "Solicitação Kit Lanche CEMEI",
                "verbose_name_plural": "Solicitações Kit Lanche CEMEI",
                "ordering": ("-criado_em",),
            },
            bases=(
                django_xworkflows.models.BaseWorkflowEnabled,
                sme_terceirizadas.dados_comuns.behaviors.TemIdentificadorExternoAmigavel,
                sme_terceirizadas.dados_comuns.behaviors.TemPrioridade,
                sme_terceirizadas.dados_comuns.behaviors.Logs,
                models.Model,
            ),
        ),
        migrations.CreateModel(
            name="SolicitacaoKitLancheEMEIdaCEMEI",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "uuid",
                    models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
                ),
                (
                    "tempo_passeio",
                    models.PositiveSmallIntegerField(
                        blank=True,
                        choices=[
                            (0, "Quatro horas"),
                            (1, "Cinco a sete horas"),
                            (2, "Oito horas"),
                        ],
                        null=True,
                    ),
                ),
                (
                    "quantidade_alunos",
                    models.PositiveSmallIntegerField(
                        validators=[django.core.validators.MinValueValidator(1)]
                    ),
                ),
                (
                    "matriculados_quando_criado",
                    models.PositiveSmallIntegerField(
                        validators=[django.core.validators.MinValueValidator(1)]
                    ),
                ),
                (
                    "alunos_com_dieta_especial_participantes",
                    models.ManyToManyField(to="escola.Aluno"),
                ),
                ("kits", models.ManyToManyField(blank=True, to="kit_lanche.KitLanche")),
                (
                    "solicitacao_kit_lanche_cemei",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="solicitacao_emei",
                        to="kit_lanche.SolicitacaoKitLancheCEMEI",
                    ),
                ),
            ],
            options={
                "verbose_name": "Solicitação Kit Lanche CEI da EMEI",
                "verbose_name_plural": "Solicitações Kit Lanche CEI da EMEI",
            },
        ),
        migrations.CreateModel(
            name="SolicitacaoKitLancheCEIdaCEMEI",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "uuid",
                    models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
                ),
                (
                    "tempo_passeio",
                    models.PositiveSmallIntegerField(
                        blank=True,
                        choices=[
                            (0, "Quatro horas"),
                            (1, "Cinco a sete horas"),
                            (2, "Oito horas"),
                        ],
                        null=True,
                    ),
                ),
                (
                    "alunos_com_dieta_especial_participantes",
                    models.ManyToManyField(to="escola.Aluno"),
                ),
                ("kits", models.ManyToManyField(blank=True, to="kit_lanche.KitLanche")),
                (
                    "solicitacao_kit_lanche_cemei",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="solicitacao_cei",
                        to="kit_lanche.SolicitacaoKitLancheCEMEI",
                    ),
                ),
            ],
            options={
                "verbose_name": "Solicitação Kit Lanche CEI da EMEI",
                "verbose_name_plural": "Solicitações Kit Lanche CEI da EMEI",
            },
        ),
        migrations.CreateModel(
            name="FaixasQuantidadesKitLancheCEIdaCEMEI",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "uuid",
                    models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
                ),
                (
                    "quantidade_alunos",
                    models.PositiveSmallIntegerField(
                        validators=[django.core.validators.MinValueValidator(1)]
                    ),
                ),
                (
                    "matriculados_quando_criado",
                    models.PositiveSmallIntegerField(
                        validators=[django.core.validators.MinValueValidator(1)]
                    ),
                ),
                (
                    "faixa_etaria",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="escola.FaixaEtaria",
                    ),
                ),
                (
                    "solicitacao_kit_lanche_cei_da_cemei",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="faixas_quantidades",
                        to="kit_lanche.SolicitacaoKitLancheCEIdaCEMEI",
                    ),
                ),
            ],
            options={
                "verbose_name": "Faixa e quantidade de alunos da CEI da solicitação kit lanche CEMEI",
                "verbose_name_plural": "Faixas e quantidade de alunos da CEI das solicitações kit lanche CEMEI",
            },
        ),
    ]
