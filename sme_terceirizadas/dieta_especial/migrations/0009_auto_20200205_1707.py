# Generated by Django 2.2.8 on 2020-02-05 20:07

import django.db.models.deletion
import django_xworkflows.models
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("escola", "0010_auto_20200122_1412"),
        ("dieta_especial", "0008_solicitacoes_ativas_inativas_por_aluno"),
    ]

    operations = [
        migrations.CreateModel(
            name="SolicitacoesDietaEspecialAtivasInativasPorAluno",
            fields=[
                (
                    "aluno",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        primary_key=True,
                        serialize=False,
                        to="escola.Aluno",
                    ),
                ),
                ("ativas", models.IntegerField()),
                ("inativas", models.IntegerField()),
            ],
            options={
                "db_table": "dietas_ativas_inativas_por_aluno",
                "managed": False,
            },
        ),
        migrations.CreateModel(
            name="Alimento",
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
                    "nome",
                    models.CharField(blank=True, max_length=100, verbose_name="Nome"),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="SubstituicaoAlimento",
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
                    "tipo",
                    models.CharField(
                        choices=[("I", "Isento"), ("S", "Substituir")], max_length=1
                    ),
                ),
                (
                    "alimento",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="dieta_especial.Alimento",
                    ),
                ),
            ],
        ),
        migrations.AlterModelOptions(
            name="solicitacaodietaespecial",
            options={
                "ordering": ("-ativo", "-criado_em"),
                "verbose_name": "Solicitação de dieta especial",
                "verbose_name_plural": "Solicitações de dieta especial",
            },
        ),
        migrations.RemoveField(
            model_name="anexo",
            name="eh_laudo_medico",
        ),
        migrations.RemoveField(
            model_name="solicitacaodietaespecial",
            name="tipos",
        ),
        migrations.AddField(
            model_name="solicitacaodietaespecial",
            name="informacoes_adicionais",
            field=models.TextField(blank=True, verbose_name="Informações Adicionais"),
        ),
        migrations.AddField(
            model_name="solicitacaodietaespecial",
            name="nome_protocolo",
            field=models.TextField(blank=True, verbose_name="Nome do Protocolo"),
        ),
        migrations.AlterField(
            model_name="solicitacaodietaespecial",
            name="aluno",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="dietas_especiais",
                to="escola.Aluno",
            ),
        ),
        migrations.AlterField(
            model_name="solicitacaodietaespecial",
            name="status",
            field=django_xworkflows.models.StateField(
                max_length=37,
                workflow=django_xworkflows.models._SerializedWorkflow(
                    initial_state="RASCUNHO",
                    name="DietaEspecialWorkflow",
                    states=[
                        "RASCUNHO",
                        "CODAE_A_AUTORIZAR",
                        "CODAE_NEGOU_PEDIDO",
                        "CODAE_AUTORIZADO",
                        "TERCEIRIZADA_TOMOU_CIENCIA",
                        "ESCOLA_CANCELOU",
                        "ESCOLA_SOLICITOU_INATIVACAO",
                        "CODAE_NEGOU_INATIVACAO",
                        "CODAE_AUTORIZOU_INATIVACAO",
                        "TERCEIRIZADA_TOMOU_CIENCIA_INATIVACAO",
                    ],
                ),
            ),
        ),
        migrations.DeleteModel(
            name="TipoDieta",
        ),
        migrations.AddField(
            model_name="substituicaoalimento",
            name="solicitacao_dieta_especial",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                to="dieta_especial.SolicitacaoDietaEspecial",
            ),
        ),
        migrations.AddField(
            model_name="substituicaoalimento",
            name="substitutos",
            field=models.ManyToManyField(
                related_name="substitutos", to="dieta_especial.Alimento"
            ),
        ),
    ]
