# Generated by Django 4.2.7 on 2024-04-22 16:20

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("imr", "0007_faixapontuacaoimr"),
    ]

    operations = [
        migrations.CreateModel(
            name="ImportacaoPlanilhaTipoPenalidade",
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
                ("conteudo", models.FileField(blank=True, default="", upload_to="")),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("PENDENTE", "PENDENTE"),
                            ("SUCESSO", "SUCESSO"),
                            ("ERRO", "ERRO"),
                            ("PROCESSADO_COM_ERRO", "PROCESSADO_COM_ERRO"),
                            ("PROCESSANDO", "PROCESSANDO"),
                            ("REMOVIDO", "REMOVIDO"),
                        ],
                        default="PENDENTE",
                        max_length=35,
                        verbose_name="status",
                    ),
                ),
                ("log", models.TextField(blank=True, default="")),
                ("resultado", models.FileField(blank=True, default="", upload_to="")),
            ],
            options={
                "verbose_name": "Arquivo para importação/atualização de tipos de penalidade",
                "verbose_name_plural": "Arquivos para importação/atualização de tipos de penalidade",
            },
        ),
    ]
