# Generated by Django 2.2.13 on 2022-06-30 08:42

import uuid

import django.db.models.deletion
import django_xworkflows.models
from django.conf import settings
from django.db import migrations, models

import sme_terceirizadas.dados_comuns.behaviors


class Migration(migrations.Migration):
    dependencies = [
        ("terceirizada", "0007_auto_20211008_1027"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("produto", "0063_auto_20220225_1559"),
    ]

    operations = [
        migrations.AlterField(
            model_name="analisesensorial",
            name="homologacao_de_produto",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="analises_sensoriais",
                to="produto.HomologacaoDoProduto",
            ),
        ),
        migrations.AlterField(
            model_name="reclamacaodeproduto",
            name="homologacao_de_produto",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="reclamacoes",
                to="produto.HomologacaoDoProduto",
            ),
        ),
        migrations.AlterField(
            model_name="respostaanalisesensorial",
            name="homologacao_de_produto",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="respostas_analise",
                to="produto.HomologacaoDoProduto",
            ),
        ),
        migrations.CreateModel(
            name="HomologacaoProduto",
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
                    "ativo",
                    models.BooleanField(default=True, verbose_name="Está ativo?"),
                ),
                (
                    "criado_em",
                    models.DateTimeField(auto_now_add=True, verbose_name="Criado em"),
                ),
                (
                    "uuid",
                    models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
                ),
                (
                    "status",
                    django_xworkflows.models.StateField(
                        max_length=45,
                        workflow=django_xworkflows.models._SerializedWorkflow(
                            initial_state="RASCUNHO",
                            name="HomologacaoProdutoWorkflow",
                            states=[
                                "RASCUNHO",
                                "CODAE_PENDENTE_HOMOLOGACAO",
                                "CODAE_HOMOLOGADO",
                                "CODAE_NAO_HOMOLOGADO",
                                "CODAE_QUESTIONADO",
                                "CODAE_PEDIU_ANALISE_SENSORIAL",
                                "CODAE_CANCELOU_ANALISE_SENSORIAL",
                                "TERCEIRIZADA_CANCELOU",
                                "HOMOLOGACAO_INATIVA",
                                "CODAE_SUSPENDEU",
                                "ESCOLA_OU_NUTRICIONISTA_RECLAMOU",
                                "CODAE_QUESTIONOU_UE",
                                "UE_RESPONDEU_QUESTIONAMENTO",
                                "CODAE_QUESTIONOU_NUTRISUPERVISOR",
                                "NUTRISUPERVISOR_RESPONDEU_QUESTIONAMENTO",
                                "CODAE_PEDIU_ANALISE_RECLAMACAO",
                                "TERCEIRIZADA_RESPONDEU_RECLAMACAO",
                                "CODAE_AUTORIZOU_RECLAMACAO",
                                "TERCEIRIZADA_CANCELOU_SOLICITACAO_HOMOLOGACAO",
                            ],
                        ),
                    ),
                ),
                ("necessita_analise_sensorial", models.BooleanField(default=False)),
                (
                    "protocolo_analise_sensorial",
                    models.CharField(blank=True, max_length=8),
                ),
                ("pdf_gerado", models.BooleanField(default=False)),
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
                    "produto",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="homologacao",
                        to="produto.Produto",
                    ),
                ),
                (
                    "rastro_terceirizada",
                    models.ForeignKey(
                        blank=True,
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="produto_homologacaoproduto_rastro_terceirizada",
                        to="terceirizada.Terceirizada",
                    ),
                ),
            ],
            options={
                "verbose_name": "Homologação de Produto",
                "verbose_name_plural": "Homologações de Produto",
                "ordering": ("-ativo", "-criado_em"),
            },
            bases=(
                django_xworkflows.models.BaseWorkflowEnabled,
                sme_terceirizadas.dados_comuns.behaviors.Logs,
                sme_terceirizadas.dados_comuns.behaviors.TemIdentificadorExternoAmigavel,
                models.Model,
            ),
        ),
        migrations.AddField(
            model_name="analisesensorial",
            name="homologacao_produto",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="analises_sensoriais",
                to="produto.HomologacaoProduto",
            ),
        ),
        migrations.AddField(
            model_name="reclamacaodeproduto",
            name="homologacao_produto",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="reclamacoes",
                to="produto.HomologacaoProduto",
            ),
        ),
        migrations.AddField(
            model_name="respostaanalisesensorial",
            name="homologacao_produto",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="respostas_analise",
                to="produto.HomologacaoProduto",
            ),
        ),
    ]
