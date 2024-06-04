# Generated by Django 4.2.7 on 2024-05-06 16:23

import uuid

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models

import sme_terceirizadas.dados_comuns.validators


class Migration(migrations.Migration):
    dependencies = [
        ("imr", "0012_utensiliomesa_editalutensiliomesa"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="tipoocorrencia",
            name="modelo_anexo",
        ),
        migrations.AddField(
            model_name="categoriaocorrencia",
            name="gera_notificacao",
            field=models.BooleanField(
                choices=[(True, "Sim"), (False, "Não")],
                default=False,
                verbose_name="Gera Notificação?",
            ),
        ),
        migrations.CreateModel(
            name="NotificacoesAssinadasFormularioBase",
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
                    "alterado_em",
                    models.DateTimeField(auto_now=True, verbose_name="Alterado em"),
                ),
                (
                    "uuid",
                    models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
                ),
                (
                    "notificacao_assinada",
                    models.FileField(
                        upload_to="IMR",
                        validators=[
                            django.core.validators.FileExtensionValidator(
                                allowed_extensions=[
                                    "PDF",
                                    "XLS",
                                    "XLSX",
                                    "DOC",
                                    "DOCX",
                                    "PNG",
                                    "JPG",
                                    "JPEG",
                                ]
                            ),
                            sme_terceirizadas.dados_comuns.validators.validate_file_size_10mb,
                        ],
                        verbose_name="Notificação Assinada",
                    ),
                ),
                (
                    "formulario_base",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notificacoes_assinadas",
                        to="imr.formularioocorrenciasbase",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="AnexosFormularioBase",
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
                    "alterado_em",
                    models.DateTimeField(auto_now=True, verbose_name="Alterado em"),
                ),
                (
                    "uuid",
                    models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
                ),
                (
                    "anexo",
                    models.FileField(
                        upload_to="IMR",
                        validators=[
                            django.core.validators.FileExtensionValidator(
                                allowed_extensions=[
                                    "PDF",
                                    "XLS",
                                    "XLSX",
                                    "DOC",
                                    "DOCX",
                                    "PNG",
                                    "JPG",
                                    "JPEG",
                                ]
                            ),
                            sme_terceirizadas.dados_comuns.validators.validate_file_size_10mb,
                        ],
                        verbose_name="Anexo",
                    ),
                ),
                (
                    "formulario_base",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="anexos",
                        to="imr.formularioocorrenciasbase",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
