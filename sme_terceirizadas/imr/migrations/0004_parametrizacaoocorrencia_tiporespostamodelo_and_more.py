# Generated by Django 4.2.7 on 2024-04-12 16:46

import uuid

import django.contrib.postgres.fields
import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("escola", "0069_logalunopordia"),
        ("cardapio", "0046_dataintervaloalteracaocardapiocemei"),
        ("imr", "0003_alter_categoriaocorrencia_perfis_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="ParametrizacaoOcorrencia",
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
                    "posicao",
                    models.PositiveSmallIntegerField(
                        blank=True,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(1)],
                    ),
                ),
                ("titulo", models.CharField(max_length=100, verbose_name="Titulo")),
                (
                    "tipo_ocorrencia",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="parametrizacoes",
                        to="imr.tipoocorrencia",
                    ),
                ),
            ],
            options={
                "verbose_name": "Parametrização de Tipo de Ocorrência",
                "verbose_name_plural": "Parametrizações de Tipo de Ocorrência",
            },
        ),
        migrations.CreateModel(
            name="TipoRespostaModelo",
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
            ],
            options={
                "verbose_name": "Tipo de Resposta (Modelo)",
                "verbose_name_plural": "Tipos de Resposta (Modelo)",
            },
        ),
        migrations.CreateModel(
            name="TipoPerguntaParametrizacaoOcorrencia",
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
                    "tipo_resposta",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="imr.tiporespostamodelo",
                        verbose_name="Tipo de resposta",
                    ),
                ),
            ],
            options={
                "verbose_name": "Tipo de Pergunta para Parametrização de Tipo de Ocorrência",
                "verbose_name_plural": "Tipos de Pergunta para Parametrização de Tipo de Ocorrência",
            },
        ),
        migrations.CreateModel(
            name="RespostaTipoAlimentacao",
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
                    "parametrizacao",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="respostas_tipos_alimentacao",
                        to="imr.parametrizacaoocorrencia",
                    ),
                ),
                (
                    "resposta",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="respostas_relatorio_imr",
                        to="cardapio.tipoalimentacao",
                    ),
                ),
            ],
            options={
                "verbose_name": "Resposta Tipo Alimentação",
                "verbose_name_plural": "Respostas Tipo Alimentação",
            },
        ),
        migrations.CreateModel(
            name="RespostaSimNaoNaoSeAplica",
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
                    "resposta",
                    models.CharField(
                        choices=[
                            ("Sim", "Sim"),
                            ("Não", "Não"),
                            ("Não se aplica", "Não se aplica"),
                        ],
                        max_length=13,
                        verbose_name="Opção",
                    ),
                ),
                (
                    "parametrizacao",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="respostas_sim_nao_nao_se_aplica",
                        to="imr.parametrizacaoocorrencia",
                    ),
                ),
            ],
            options={
                "verbose_name": "Resposta Sim/Não/Não se aplica",
                "verbose_name_plural": "Respostas Sim/Não/Não se aplica",
            },
        ),
        migrations.CreateModel(
            name="RespostaSimNao",
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
                    "resposta",
                    models.CharField(
                        choices=[("Sim", "Sim"), ("Não", "Não")],
                        max_length=3,
                        verbose_name="Opção",
                    ),
                ),
                (
                    "parametrizacao",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="respostas_sim_nao",
                        to="imr.parametrizacaoocorrencia",
                    ),
                ),
            ],
            options={
                "verbose_name": "Resposta Sim/Não",
                "verbose_name_plural": "Respostas Sim/Não",
            },
        ),
        migrations.CreateModel(
            name="RespostaPeriodo",
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
                    "parametrizacao",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="respostas_periodo",
                        to="imr.parametrizacaoocorrencia",
                    ),
                ),
                (
                    "resposta",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="respostas_relatorio_imr",
                        to="escola.periodoescolar",
                    ),
                ),
            ],
            options={
                "verbose_name": "Resposta Período",
                "verbose_name_plural": "Respostas Período",
            },
        ),
        migrations.CreateModel(
            name="RespostaFaixaEtaria",
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
                    "parametrizacao",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="respostas_faixa_etaria",
                        to="imr.parametrizacaoocorrencia",
                    ),
                ),
                (
                    "resposta",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="respostas_relatorio_imr",
                        to="escola.faixaetaria",
                    ),
                ),
            ],
            options={
                "verbose_name": "Resposta Faixa Etária",
                "verbose_name_plural": "Respostas Faixa Etária",
            },
        ),
        migrations.CreateModel(
            name="RespostaDatas",
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
                    "resposta",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.DateField(), size=None
                    ),
                ),
                (
                    "parametrizacao",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="respostas_datas",
                        to="imr.parametrizacaoocorrencia",
                    ),
                ),
            ],
            options={
                "verbose_name": "Resposta Datas",
                "verbose_name_plural": "Respostas Datas",
            },
        ),
        migrations.CreateModel(
            name="RespostaCampoTextoSimples",
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
                ("resposta", models.CharField(max_length=500)),
                (
                    "parametrizacao",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="respostas_campo_texto_simples",
                        to="imr.parametrizacaoocorrencia",
                    ),
                ),
            ],
            options={
                "verbose_name": "Resposta Campo Texto Simples",
                "verbose_name_plural": "Respostas Campo Texto Simples",
            },
        ),
        migrations.CreateModel(
            name="RespostaCampoTextoLongo",
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
                ("resposta", models.TextField()),
                (
                    "parametrizacao",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="respostas_campo_texto_longo",
                        to="imr.parametrizacaoocorrencia",
                    ),
                ),
            ],
            options={
                "verbose_name": "Resposta Campo Texto Longo",
                "verbose_name_plural": "Respostas Campo Texto Longo",
            },
        ),
        migrations.CreateModel(
            name="RespostaCampoNumerico",
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
                ("resposta", models.FloatField()),
                (
                    "parametrizacao",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="respostas_campo_numerico",
                        to="imr.parametrizacaoocorrencia",
                    ),
                ),
            ],
            options={
                "verbose_name": "Resposta Campo Numérico",
                "verbose_name_plural": "Respostas Campo Numérico",
            },
        ),
        migrations.AddField(
            model_name="parametrizacaoocorrencia",
            name="tipo_pergunta",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="parametrizacoes",
                to="imr.tipoperguntaparametrizacaoocorrencia",
            ),
        ),
    ]
