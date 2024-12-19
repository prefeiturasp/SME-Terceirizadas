# Generated by Django 2.2.13 on 2021-11-04 11:27

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("dieta_especial", "0044_merge_20211029_1936"),
    ]

    operations = [
        migrations.CreateModel(
            name="ArquivoCargaUsuariosEscola",
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
                "verbose_name": "Arquivo para importação de usuários Diretor e Assistente Diretor",
                "verbose_name_plural": "Arquivos para importação de usuários Diretor e Assistente Diretor",
            },
        ),
    ]