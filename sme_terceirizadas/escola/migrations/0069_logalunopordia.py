# Generated by Django 4.2.7 on 2024-03-27 14:55

import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("escola", "0068_add_historico_matricula_aluno"),
    ]

    operations = [
        migrations.CreateModel(
            name="LogAlunoPorDia",
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
                (
                    "aluno",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="logs_alunos_por_dia",
                        to="escola.aluno",
                    ),
                ),
                (
                    "log_alunos_matriculados_faixa_dia",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="logs_alunos_por_dia",
                        to="escola.logalunosmatriculadosfaixaetariadia",
                    ),
                ),
            ],
            options={
                "verbose_name": "Log aluno por dia",
                "verbose_name_plural": "Logs alunos por dia",
                "ordering": ("criado_em",),
            },
        ),
    ]
